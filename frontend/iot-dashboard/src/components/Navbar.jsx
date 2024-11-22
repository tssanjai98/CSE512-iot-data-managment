import React from "react";
import { Link, useLocation } from "react-router-dom";
import "../styles/navbar.css";

const Navbar = () => {
    const location = useLocation();

    return (
        <nav className="navbar">
            <div className="navbar-logo">IoT App</div>
            <div className="navbar-links">
                <Link 
                    to="/" 
                    className={location.pathname === "/" ? "active" : ""}
                >
                    Dashboard
                </Link>
                <Link 
                    to="/query-tool" 
                    className={location.pathname === "/query-tool" ? "active" : ""}
                >
                    Query Tool
                </Link>
            </div>
        </nav>
    );
};

export default Navbar;
