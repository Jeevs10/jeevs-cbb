declare module 'react-simple-maps' {
  export interface ComposableMapProps {
    children?: React.ReactNode;
    projection?: string;
    projectionConfig?: any;
    style?: React.CSSProperties;
  }

  export const ComposableMap: React.FC<ComposableMapProps>;

  export interface GeographiesProps {
    geography: string | object;
    children?: (props: { geographies: any[] }) => React.ReactNode;
  }

  export const Geographies: React.FC<GeographiesProps>;

  export interface GeographyProps {
    geography: any;
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    style?: any;
  }

  export const Geography: React.FC<GeographyProps>;

  export interface MarkerProps {
    coordinates: [number, number];
    children?: React.ReactNode;
  }

  export const Marker: React.FC<MarkerProps>;
}
