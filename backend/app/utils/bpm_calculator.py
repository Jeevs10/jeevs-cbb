"""BPM 2.0 Calculator for college basketball players.

This module implements Box Plus-Minus (BPM) 2.0 calculations using ridge regression
trained on historical RAPM data. BPM estimates a player's contribution to their team's
performance per 100 possessions.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os


class BPMCalculator:
    """Calculator for Box Plus-Minus (BPM) 2.0 metric using ridge regression."""
    
    # Feature columns to use for ridge regression
    FEATURE_COLUMNS = [
        'Points', 'Rebounds Total', 'Assists', 'Steals', 'Blocks', 'Turnovers',
        'FieldGoals Made', 'FieldGoals Attempted', 'FreeThrows Made', 'FreeThrows Attempted',
        'ThreePointFieldGoals Made', 'ThreePointFieldGoals Attempted',
        'TwoPointFieldGoals Made', 'TwoPointFieldGoals Attempted',
        'Rebounds Offensive', 'Rebounds Defensive',
        'OffensiveReboundPct', 'Usage', 'TrueShootingPct', 'AssistsTurnoverRatio',
        'EffectiveFieldGoalPct', 'Minutes', 'Games'
    ]
    
    # RAPM target columns in enriched data
    RAPM_TARGETS = ['adj_rapm_margin', 'off_adj_rapm', 'def_adj_rapm']
    
    def __init__(self):
        """Initialize the BPM calculator."""
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.is_trained = False
    
    def train_ridge_regression(self, enriched_df: pd.DataFrame, alpha: float = 1.0) -> Dict[str, Any]:
        """Train ridge regression model on enriched data with RAPM targets.
        
        Args:
            enriched_df: DataFrame with enriched player data including RAPM metrics
            alpha: Ridge regularization parameter
            
        Returns:
            Dictionary with training metrics
        """
        training_data = self._prepare_training_data(enriched_df)
        
        if training_data is None or len(training_data['features']) < 100:
            raise ValueError("Insufficient enriched data for training (need at least 100 samples)")
        
        X = training_data['features']
        y = training_data['target']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        n_features = X_train_scaled.shape[1]
        identity = np.eye(n_features)

        XtX = X_train_scaled.T @ X_train_scaled
        Xty = X_train_scaled.T @ y_train
        ridge_coefficients = np.linalg.solve(XtX + alpha * identity, Xty)

        self.model = {
            'coefficients': ridge_coefficients,
            'intercept': np.mean(y_train - X_train_scaled @ ridge_coefficients)
        }

        train_predictions = X_train_scaled @ ridge_coefficients + self.model['intercept']
        test_predictions = X_test_scaled @ ridge_coefficients + self.model['intercept']

        train_score = 1 - np.sum((y_train - train_predictions)**2) / np.sum((y_train - np.mean(y_train))**2)
        test_score = 1 - np.sum((y_test - test_predictions)**2) / np.sum((y_test - np.mean(y_test))**2)

        self.feature_names = training_data['feature_names']
        self.is_trained = True

        coefficients = dict(zip(self.feature_names, self.model['coefficients']))
        
        return {
            'train_r2': train_score,
            'test_r2': test_score,
            'n_samples': len(X),
            'n_features': len(self.feature_names),
            'coefficients': coefficients,
            'intercept': self.model['intercept']
        }
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Prepare training data from enriched DataFrame.
        
        Args:
            df: Enriched player DataFrame
            
        Returns:
            Dictionary with features, target, and feature names
        """
        rapm_target = None
        for target in self.RAPM_TARGETS:
            if target in df.columns:
                rapm_target = target
                break
        
        if rapm_target is None:
            return None

        df_filtered = df[
            (df[rapm_target].notna()) &
            (df['Minutes'].notna()) &
            (df['Minutes'] >= 100) &
            (df['Games'].notna()) &
            (df['Games'] >= 10)
        ].copy()
        
        if len(df_filtered) == 0:
            return None

        column_mapping = {
        }

        features = []
        feature_names = []
        
        for col in self.FEATURE_COLUMNS:
            if col in df_filtered.columns:
                feature_values = df_filtered[col].fillna(0).values
                features.append(feature_values)
                feature_names.append(col)
            elif col in column_mapping and column_mapping[col] in df_filtered.columns:
                feature_values = df_filtered[column_mapping[col]].fillna(0).values
                features.append(feature_values)
                feature_names.append(col)
        
        if not features:
            return None
        
        X = np.column_stack(features)
        y = df_filtered[rapm_target].values
        
        return {
            'features': X,
            'target': y,
            'feature_names': feature_names
        }
    
    def predict_bpm(self, player_stats: Dict[str, Any]) -> Optional[float]:
        """Predict BPM for a player using trained ridge regression model.
        
        Args:
            player_stats: Dictionary containing player statistics
            
        Returns:
            Predicted BPM value or None if model not trained or insufficient data
        """
        if not self.is_trained:
            return None

        features = self._prepare_features(player_stats)
        if features is None:
            return None

        features_scaled = self.scaler.transform(features.reshape(1, -1))
        bpm = features_scaled @ self.model['coefficients'] + self.model['intercept']
        bpm = bpm[0]
        
        return round(bpm, 2)
    
    def _prepare_features(self, player_stats: Dict[str, Any]) -> Optional[np.ndarray]:
        """Prepare feature vector for prediction.
        
        Args:
            player_stats: Dictionary containing player statistics
            
        Returns:
            Feature vector or None if insufficient data
        """
        minutes = player_stats.get('Minutes', 0)
        games = player_stats.get('Games', 0)
        
        if minutes < 100 or games < 10:
            return None

        features = []
        for col in self.FEATURE_COLUMNS:
            value = player_stats.get(col, 0)
            if pd.isna(value):
                value = 0
            features.append(value)
        
        return np.array(features)
    
    def predict_bpm_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict BPM for all players in a DataFrame.
        
        Args:
            df: DataFrame containing player statistics
            
        Returns:
            DataFrame with BPM column added
        """
        df = df.copy()
        
        # BPM calculation disabled - returning DataFrame without BPM
        return df
    
    def calculate_vorp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate VORP (Value Over Replacement Player) for all players.
        
        VORP = BPM * (Minutes / (Games * 36))
        This estimates a player's total value compared to a replacement player.
        
        Args:
            df: DataFrame containing player statistics with BPM column
            
        Returns:
            DataFrame with VORP column added
        """
        df = df.copy()

        vorp_values = []
        for _, row in df.iterrows():
            player_dict = row.to_dict()
            vorp = self._calculate_player_vorp(player_dict)
            vorp_values.append(vorp)
        
        df['VORP'] = vorp_values
        return df
    
    def _calculate_player_vorp(self, player_stats: Dict[str, Any]) -> Optional[float]:
        """Calculate VORP for a single player.
        
        Args:
            player_stats: Dictionary containing player statistics
            
        Returns:
            VORP value or None if insufficient data
        """
        try:
            bpm = player_stats.get('BPM', 0)
            minutes = player_stats.get('Minutes', 0)
            games = player_stats.get('Games', 0)
            
            if pd.isna(bpm) or pd.isna(minutes) or pd.isna(games):
                return None
            
            if minutes < 100 or games < 10:
                return None

            vorp = bpm * (minutes / (games * 36))
            
            return round(vorp, 2)
            
        except Exception:
            return None
    
    def _predict_heuristic_bpm(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fallback heuristic BPM prediction when model is not trained."""
        df = df.copy()

        return df
    
    def _calculate_heuristic_bpm(self, player_stats: Dict[str, Any]) -> Optional[float]:
        """Calculate heuristic BPM as fallback.
        
        Args:
            player_stats: Dictionary containing player statistics
            
        Returns:
            BPM value or None if insufficient data
        """
        try:
            minutes = player_stats.get('Minutes', 0)
            games = player_stats.get('Games', 0)
            
            if minutes < 100 or games < 10:
                return None

            estimated_possessions = minutes * 0.85
            if estimated_possessions <= 0:
                return None
            
            # Get stats
            points = player_stats.get('Points', 0)
            rebounds_total = player_stats.get('Rebounds Total', 0)
            assists = player_stats.get('Assists', 0)
            steals = player_stats.get('Steals', 0)
            blocks = player_stats.get('Blocks', 0)
            turnovers = player_stats.get('Turnovers', 0)
            usage_rate = player_stats.get('Usage', 0)
            ts_pct = player_stats.get('TrueShootingPct', 0)

            points_per_100 = (points / estimated_possessions) * 100
            rebounds_per_100 = (rebounds_total / estimated_possessions) * 100
            assists_per_100 = (assists / estimated_possessions) * 100
            steals_per_100 = (steals / estimated_possessions) * 100
            blocks_per_100 = (blocks / estimated_possessions) * 100
            turnovers_per_100 = (turnovers / estimated_possessions) * 100

            bpm = (
                0.08 * points_per_100 +
                0.06 * rebounds_per_100 +
                0.09 * assists_per_100 +
                0.15 * steals_per_100 +
                0.12 * blocks_per_100 -
                0.18 * turnovers_per_100 +
                0.02 * usage_rate +
                0.2 * (ts_pct - 0.5)
            )
            
            return round(bpm, 2)
            
        except Exception:
            return None
    
    def save_model(self, filepath: str):
        """Save trained model and scaler to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath: str):
        """Load trained model and scaler from disk.
        
        Args:
            filepath: Path to load the model from
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']


# Global instance
_bpm_calculator_instance = None

def get_bpm_calculator() -> BPMCalculator:
    """Get or create global BPM calculator instance."""
    global _bpm_calculator_instance
    if _bpm_calculator_instance is None:
        _bpm_calculator_instance = BPMCalculator()
    return _bpm_calculator_instance
