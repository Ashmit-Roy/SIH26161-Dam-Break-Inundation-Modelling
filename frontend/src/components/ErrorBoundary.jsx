import React from "react";

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Dashboard caught runtime error:", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: "100vh",
          background: "#090d16",
          color: "#f8fafc",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "2rem",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          <div style={{
            maxWidth: "600px",
            background: "#1e293b",
            border: "1px solid #ef4444",
            borderRadius: "12px",
            padding: "2rem",
            boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
          }}>
            <h2 style={{ color: "#ef4444", marginTop: 0, display: "flex", alignItems: "center", gap: "8px" }}>
              ⚠️ Dashboard Runtime Error
            </h2>
            <p style={{ color: "#cbd5e1", fontSize: "0.95rem" }}>
              The application encountered an unexpected runtime issue during rendering.
            </p>
            <div style={{
              background: "#0f172a",
              padding: "12px",
              borderRadius: "6px",
              fontSize: "0.85rem",
              fontFamily: "monospace",
              color: "#fca5a5",
              margin: "1rem 0",
              overflowX: "auto",
            }}>
              {this.state.error?.toString() || "Unknown error"}
            </div>
            <button
              onClick={() => window.location.reload()}
              style={{
                background: "#e94560",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                padding: "8px 16px",
                fontWeight: "bold",
                cursor: "pointer",
              }}
            >
              🔄 Reload Dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
