"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { cn } from "@/lib/utils";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  className?: string;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Error caught by boundary
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className={cn(
          "p-4 border-2 border-black bg-red-100",
          this.props.className
        )}>
          <h2 className="text-lg font-bold mb-2">Something went wrong</h2>
          <details className="text-sm">
            <summary className="cursor-pointer">Error details</summary>
            <pre className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
              {this.state.error?.message}
            </pre>
          </details>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-black text-white border border-black hover:bg-gray-800"
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
