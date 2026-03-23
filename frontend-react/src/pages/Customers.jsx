import React, { useEffect, useState } from 'react';
import { MoreVertical } from 'lucide-react';
import AddCustomerModal from '../components/AddCustomerModal';

export default function Customers() {
    const [customers, setCustomers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchCustomers = () => {
        setLoading(true);
        fetch('/api/v1/customers')
            .then(res => res.json())
            .then(data => {
                setCustomers(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load customers", err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchCustomers();
    }, []);

    if (loading && customers.length === 0) return <div className="loading-state"><span className="spinner"></span> Loading customers...</div>;

    return (
        <section className="page active" id="page-customers">
            <div className="page-actions">
                <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>+ Add Customer</button>
            </div>

            <AddCustomerModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onComplete={fetchCustomers}
            />
            <div className="table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>Customer</th>
                            <th>Company</th>
                            <th>Industry</th>
                            <th>Size</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {customers.map(c => (
                            <tr key={c.customer_id}>
                                <td>
                                    <div className="customer-name">{c.name}</div>
                                    <div className="customer-email">{c.email}</div>
                                </td>
                                <td>{c.company}</td>
                                <td><span className="badge badge-muted">{c.industry || 'Unknown'}</span></td>
                                <td>{c.company_size || 'N/A'}</td>
                                <td>{new Date(c.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button className="btn-icon">
                                        <MoreVertical size={16} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {customers.length === 0 && (
                            <tr><td colSpan="6" style={{ textAlign: 'center', padding: '20px' }}>No customers found.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </section>
    );
}
