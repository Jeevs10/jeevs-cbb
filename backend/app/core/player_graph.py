import os
import pandas as pd
from collections import defaultdict
import networkx as nx
import random

from app.core.roster_data import get_roster_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class PlayerGraph:
    """Graph of players connected by teammate relationships"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.player_info = {}
        self._loaded = False
    
    def load_from_roster_data(self, conferences=None, years=None):
        """Build graph from roster data - players connected if they were ever teammates

        Args:
            conferences: Optional list of conference names to filter by
            years: Optional list of years to include
        """
        if conferences:
            pass
        if years:
            pass

        roster_df = self._load_roster_data(conferences=conferences, years=years)
        
        if roster_df.empty:
            return

        player_data = {}
        for _, row in roster_df.iterrows():
            player_id = str(row['Sourceid'])
            if player_id not in player_data:
                player_data[player_id] = {
                    'name': row.get('Name', 'Unknown'),
                    'teams': set(),
                    'years': set(),
                    'positions': set(),
                    'heights': set(),
                    'hometowns': set(),
                    'conferences': set()
                }
            player_data[player_id]['teams'].add(row.get('Team', 'Unknown'))
            player_data[player_id]['years'].add(int(row.get('year', 0)))
            if pd.notna(row.get('Position')):
                player_data[player_id]['positions'].add(row.get('Position'))
            if pd.notna(row.get('Height')):
                player_data[player_id]['heights'].add(row.get('Height'))
            if pd.notna(row.get('HometownCity')):
                hometown = row.get('HometownCity', '')
                state = row.get('HometownState', '')
                if state:
                    hometown += f", {state}"
                player_data[player_id]['hometowns'].add(hometown)
            if pd.notna(row.get('Conference')):
                player_data[player_id]['conferences'].add(row.get('Conference'))

        for player_id, info in player_data.items():
            self.player_info[player_id] = {
                'id': player_id,
                'name': info['name'],
                'teams': list(info['teams']),
                'years': sorted(list(info['years'])),
                'Position': list(info['positions'])[0] if info['positions'] else None,
                'roster_height': list(info['heights'])[0] if info['heights'] else None,
                'hometown': list(info['hometowns'])[0] if info['hometowns'] else None,
                'conf': list(info['conferences'])[0] if info['conferences'] else None
            }

        grouped = roster_df.groupby(['Team', 'year'])

        for (team, year), group in grouped:
            player_ids = group['Sourceid'].tolist()

            for i in range(len(player_ids)):
                for j in range(i + 1, len(player_ids)):
                    pid1 = str(player_ids[i])
                    pid2 = str(player_ids[j])
                    if not self.graph.has_edge(pid1, pid2):
                        self.graph.add_edge(pid1, pid2)
        
        self._loaded = True
    
    def _load_roster_data(self, conferences=None, years=None):
        """Load roster info from all available years, with optional filters

        Args:
            conferences: Optional list of conference names to filter by
            years: Optional list of years to include
        """
        df = get_roster_data(years=years)
        if df.empty:
            return pd.DataFrame()

        # Filter out players without conferences to reduce graph size
        df = df[df['Conference'].notna() & (df['Conference'] != '')].copy()

        # Filter by conference if specified
        if conferences:
            df = df[df['Conference'].isin(conferences)]

        if 'Sourceid' in df.columns:
            df['Sourceid'] = df['Sourceid'].astype(str)

        return df
    
    def reload_with_filters(self, conferences=None, years=None):
        """Reload the graph with new filters
        
        Args:
            conferences: Optional list of conference names to filter by
            years: Optional list of years to include
        """
        # Clear existing graph and player info
        self.graph = nx.Graph()
        self.player_info = {}
        self._loaded = False
        
        # Reload with new filters
        self.load_from_roster_data(conferences=conferences, years=years)
    
    def get_random_reachable_pair(self, min_distance=3, max_distance=6):
        if not self._loaded:
            self.load_from_roster_data()
        
        if self.graph.number_of_nodes() == 0:
            raise ValueError("Graph is empty, cannot generate pair")
        
        # Optimization: Use BFS to find pairs within distance range more efficiently
        # Instead of checking all nodes, do BFS from random start until we find valid targets
        max_attempts = 50
        nodes_list = list(self.graph.nodes())
        
        for _ in range(max_attempts):
            # Pick random start player
            start_id = random.choice(nodes_list)
            
            # Use BFS to find all nodes within max_distance
            # This is much faster than calculating shortest path for all nodes
            try:
                lengths = nx.single_source_shortest_path_length(self.graph, start_id, cutoff=max_distance)
                
                # Filter nodes within our desired range
                nodes_in_range = [
                    (node_id, length) 
                    for node_id, length in lengths.items() 
                    if min_distance <= length <= max_distance
                ]
                
                if nodes_in_range:
                    target_id, distance = random.choice(nodes_in_range)
                    return {
                        'start_player': self.player_info.get(start_id, {'id': start_id, 'name': 'Unknown'}),
                        'end_player': self.player_info.get(target_id, {'id': target_id, 'name': 'Unknown'}),
                        'distance': distance
                    }
            except:
                continue
        
        # If we couldn't find a pair within the requested distance range, raise an error
        raise ValueError(f"No pair found with those settings. Try a wider range.")
    
    def get_player_info(self, player_id):
        """Get player info from the graph (including all teams and years)"""
        if not self._loaded:
            self.load_from_roster_data()
        
        pid = str(player_id)
        return self.player_info.get(pid, None)

    def are_teammates(self, player_id1, player_id2):
        """Check if two players were teammates (connected in graph)"""
        if not self._loaded:
            self.load_from_roster_data()
        
        pid1 = str(player_id1)
        pid2 = str(player_id2)
        
        return self.graph.has_edge(pid1, pid2)
    
    def get_teammate_info(self, player_id1, player_id2):
        """Get info about when two players were teammates"""
        if not self._loaded:
            self.load_from_roster_data()
        
        pid1 = str(player_id1)
        pid2 = str(player_id2)
        
        if not self.graph.has_edge(pid1, pid2):
            return None
        
        edge_data = self.graph.get_edge_data(pid1, pid2)
        # Convert numpy types to native Python types for serialization
        return {k: int(v) if hasattr(v, 'dtype') else v for k, v in edge_data.items()}
    
    def get_shortest_path(self, player_id1, player_id2):
        """Get shortest path between two players"""
        if not self._loaded:
            self.load_from_roster_data()
        
        pid1 = str(player_id1)
        pid2 = str(player_id2)
        
        try:
            path = nx.shortest_path(self.graph, pid1, pid2)
            # Convert to player info and ensure values are serializable
            path_info = []
            for pid in path:
                info = self.player_info.get(pid, {'id': pid, 'name': 'Unknown'})
                # Convert numpy types to native Python types
                serializable_info = {}
                for k, v in info.items():
                    if hasattr(v, 'dtype'):
                        serializable_info[k] = int(v) if isinstance(v, (np.integer, np.int64)) else float(v)
                    else:
                        serializable_info[k] = v
                path_info.append(serializable_info)
            return path_info
        except nx.NetworkXNoPath:
            return None


# Global instance
player_graph = PlayerGraph()
