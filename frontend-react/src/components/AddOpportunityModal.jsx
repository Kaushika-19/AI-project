import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export default function AddOpportunityModal({ isOpen, onClose, onComplete }) {
    const [customers, setCustomers] = useState([]);
    const [formData, setFormData] = useState({
        customer_id: '',
        opportunity_name: '',
        deal_value: 0,
        product_interest: '',
        stage: 'LEAD',
        status: 'OPEN',
        probability: 10
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetch('/api/v1/customers')
                .then(res => res.json())
                .then(data => setCustomers(data))
                .catch(err => console.error(err));
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await fetch('/api/v1/opportunities', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            if (res.ok) {
                onComplete();
                onClose();
            } else {
                const err = await res.json();
                alert(err.detail || "Failed to create opportunity");
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
                    <h2>New Sales Opportunity</h2>
                    <button className="modal-close" onClick={onClose}><X size={20} /></button>
                </div>
                <form onSubmit={handleSubmit} className="modal-body">
                    <div className="detail-grid">
                        <div className="detail-item full-width">
                            <label className="detail-label">Customer</label>
                            <select
                                className="filter-select"
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                                value={formData.customer_id}
                                onChange={e => setFormData({ ...formData, customer_id: e.target.value })}
                                required
                            >
                                <option value="">Select a customer...</option>
                                {customers.map(c => (
                                    <option key={c.customer_id} value={c.customer_id}>{c.name} ({c.company})</option>
                                ))}
                            </select>
                        </div>
                        <div className="detail-item full-width">
                            <label className="detail-label">Opportunity Name</label>
                            <input
                                type="text"
                                className="filter-select"
                                value={formData.opportunity_name}
                                onChange={e => setFormData({ ...formData, opportunity_name: e.target.value })}
                                required
                                placeholder="e.g. Enterprise License Expansion"
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                            />
                        </div>
                        <div className="detail-item">
                            <label className="detail-label">Deal Value ($)</label>
                            <input
                                type="number"
                                className="filter-select"
                                value={formData.deal_value}
                                onChange={e => setFormData({ ...formData, deal_value: parseFloat(e.target.value) })}
                                required
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                            />
                        </div>
                        <div className="detail-item">
                            <label className="detail-label">Initial Probability (%)</label>
                            <input
                                type="number"
                                className="filter-select"
                                value={formData.probability}
                                onChange={e => setFormData({ ...formData, probability: parseInt(e.target.value) })}
                                required
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                            />
                        </div>
                        <div className="detail-item full-width">
                            <label className="detail-label">Product Interest</label>
                            <input
                                type="text"
                                className="filter-select"
                                value={formData.product_interest}
                                onChange={e => setFormData({ ...formData, product_interest: e.target.value })}
                                placeholder="e.g. Sales Accelerator Suite"
                                style={{ width: '100%', backgroundImage: 'none', paddingLeft: '12px' }}
                            />
                        </div>
                    </div>
                    <div style={{ marginTop: '24px' }}>
                        <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
                            {loading ? "Creating..." : "Create Opportunity"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
