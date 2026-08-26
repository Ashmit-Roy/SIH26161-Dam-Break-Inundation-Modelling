import React from "react";

function Header() {
  return (
    <header className="main-header">
      <div className="header-content">
        <h1 className="header-title">
          <span className="icon-fill">🌊</span>Dam Break Inundation<br/>
          <span className="sub-title">Modelling System</span>
        </h1>
        <p className="header-desc">
          SIH 26161 · Smart India Hackathon 2026 · Flood Risk Assessment
        </p>
      </div>
    </header>
  );
}

export default Header;