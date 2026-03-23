import React, { useState } from 'react';
import { X, Send } from 'lucide-react';

export default function AddCustomerModal({ isOpen, onClose, onComplete }) {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        company: '',
        industry: '',
        company_size: ''
    });
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await fetch('/api/v1/customers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            if (res.ok) {
                onComplete();
                onClose();
            } else {
                const err = await res.json();
                alert(err.detail || "Failed to create customer");
            }
        } catch (err) {
            console.error(err);
            alert("Connection error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay active" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Add New Customer</h2>
                    <button className="modal-close" onClick={onClose}><X size={20} /></button>
                </div>
                <form onSubmit={handleSubmit} className="modal-body">
                    <div className="detail-grid">
                        <div className="detail-item full-width">
                            <label className="detail-label">Full Name</label>
                            <input
                                type="text"
                                className="filter-select"
                                value={formData.name}
                                onChange={e => setFormData({ ...formData, name: e.target.value })}
                                required
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                            />
                        </div>
                        <div className="detail-item full-width">
                            <label className="detail-label">Email Address</label>
                            <input
                                type="email"
                                className="filter-select"
                                value={formData.email}
                                onChange={e => setFormData({ ...formData, email: e.target.value })}
                                required
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                            />
                        </div>
                        <div className="detail-item full-width">
                            <label className="detail-label">Company Name</label>
                            <input
                                type="text"
                                className="filter-select"
                                value={formData.company}
                                onChange={e => setFormData({ ...formData, company: e.target.value })}
                                required
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                            />
                        </div>
                        <div className="detail-item">
                            <label className="detail-label">Industry</label>
                            <select
                                className="filter-select"
                                value={formData.industry}
                                onChange={e => setFormData({ ...formData, industry: e.target.value })}
                            >
                                <option value="">Select...</option>
                                <option value="Tech">Tech</option>
                                <option value="Finance">Finance</option>
                                <option value="Healthcare">Healthcare</option>
                                <option value="Real Estate">Real Estate</option>
                                <option value="Retail">Retail</option>
                            </select>
                        </div>
                        <div className="detail-item">
                            <label className="detail-label">Size</label>
                            <select
                                className="filter-select"
                                value={formData.company_size}
                                onChange={e => setFormData({ ...formData, company_size: e.target.value })}
                            >
                                <option value="">Select...</option>
                                <option value="1-10">1-10</option>
                                <option value="11-50">11-50</option>
                                <option value="51-200">51-200</option>
                                <option value="201-1000">201-1000</option>
                                <option value="1000+">1000+</option>
                            </select>
                        </div>
                    </div>
                    <div style={{ marginTop: '24px' }}>
                        <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
                            {loading ? "Adding..." : "Save Customer"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
