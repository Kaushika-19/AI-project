import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, MessageSquare, BrainCircuit, Activity, LineChart } from 'lucide-react';

export default function Sidebar({ isOpen, setIsOpen }) {
    return (
        <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`} id="sidebar">
            <div className="sidebar-brand">
                <div className="brand-icon">N</div>
                <span className="brand-text">NeoVerse</span>
            </div>

            <nav className="sidebar-nav">
                <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={() => window.innerWidth <= 768 && setIsOpen(false)}>
                    <LayoutDashboard size={20} />
                    <span>Dashboard</span>
                </NavLink>
                <NavLink to="/customers" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={() => window.innerWidth <= 768 && setIsOpen(false)}>
                    <Users size={20} />
                    <span>Customers</span>
                </NavLink>
                <NavLink to="/pipeline" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={() => window.innerWidth <= 768 && setIsOpen(false)}>
                    <LineChart size={20} />
                    <span>Pipeline</span>
                </NavLink>
                <NavLink to="/insights" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={() => window.innerWidth <= 768 && setIsOpen(false)}>
                    <BrainCircuit size={20} />
                    <span>AI Insights</span>
                </NavLink>
                <NavLink to="/actions" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={() => window.innerWidth <= 768 && setIsOpen(false)}>
                    <Activity size={20} />
                    <span>Actions</span>
                </NavLink>
            </nav>

            <div className="sidebar-footer">
                <div className="connection-status">
                    <span className="status-dot"></span>
                    <span>Connected</span>
                </div>
            </div>
        </aside>
    );
}
