import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export class AppErrorBoundary extends Component<Props, State> {
  state: State = {
    hasError: false,
    message: ""
  };

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      message: error.message || "The app hit an unexpected error."
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("App render failure", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="center-screen">
          <div className="panel stack gap-md">
            <h2>Something went wrong</h2>
            <p>{this.state.message}</p>
            <p>Reload the app to recover. If this keeps happening, the last action needs investigated.</p>
            <button
              className="primary-btn"
              onClick={() => {
                window.location.reload();
              }}
            >
              Reload App
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
