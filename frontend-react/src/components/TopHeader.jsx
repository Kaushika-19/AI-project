import React from 'react';
import { Menu, Search } from 'lucide-react';

export default function TopHeader({ title, onMenuToggle }) {
    return (
        <header className="top-header">
            <div className="header-left">
                <button className="menu-toggle" onClick={onMenuToggle}>
                    <Menu size={22} />
                </button>
                <h1 className="page-title">{title}</h1>
            </div>
            <div className="header-right">
                <div className="search-box">
                    <Search size={18} />
                    <input type="text" placeholder="Search..." />
                </div>
            </div>
        </header>
    );
}
