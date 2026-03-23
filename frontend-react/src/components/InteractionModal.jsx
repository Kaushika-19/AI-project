import React, { useState, useEffect } from 'react';
import { X, Upload, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export default function InteractionModal({ isOpen, onClose, onComplete }) {
    const [opportunities, setOpportunities] = useState([]);
    const [selectedOpp, setSelectedOpp] = useState('');
    const [email, setEmail] = useState('');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('idle'); // idle, uploading, complete, error
    const [errorMessage, setErrorMessage] = useState('');
    const [result, setResult] = useState(null);
    const [activeTab, setActiveTab] = useState('audio'); // 'audio' or 'text'
    const [transcript, setTranscript] = useState('');
    const [selectedRecommendation, setSelectedRecommendation] = useState(null); // null if custom, 0, 1, 2 if AI
    const [customRecommendation, setCustomRecommendation] = useState({
        title: '',
        action: '',
        reason: '',
        priority: 'Medium',
        date: new Date().toISOString().split('T')[0]
    });
    const [sendAt, setSendAt] = useState(() => {
        const now = new Date();
        now.setHours(9, 0, 0, 0);
        return now.toISOString().slice(0, 16); // "YYYY-MM-DDTHH:MM" for datetime-local
    });

    // New Deal States
    const [newDealData, setNewDealData] = useState({
        customerName: '',
        customerEmail: '',
        company: '',
        opportunityName: ''
    });

    useEffect(() => {
        if (isOpen) {
            fetch('/api/v1/pipeline')
                .then(res => res.json())
                .then(data => {
                    // Only show active opportunities
                    const activeOpps = data.filter(opp =>
                        opp.status !== 'CLOSED_WON' && opp.status !== 'CLOSED_LOST'
                    );
                    setOpportunities(activeOpps);
                })
                .catch(err => console.error(err));
        }
    }, [isOpen]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedOpp) return;
        if (activeTab === 'audio' && !file) return;
        if (activeTab === 'text' && !transcript) return;

        setLoading(true);
        setStatus('uploading');

        try {
            let finalOppId = selectedOpp;

            // 1. Create New Deal if requested
            if (selectedOpp === 'NEW_DEAL') {
                // Create Customer
                const custRes = await fetch('/api/v1/customers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: newDealData.customerName,
                        email: newDealData.customerEmail,
                        company: newDealData.company
                    })
                });
                if (!custRes.ok) {
                    const err = await custRes.json().catch(() => ({}));
                    throw new Error(err.detail || 'Failed to create customer');
                }
                const customer = await custRes.json();
                const actualCustomerId = customer.customer_id || customer.id;

                // Create Opportunity
                const oppRes = await fetch('/api/v1/opportunities', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer_id: actualCustomerId,
                        opportunity_name: newDealData.opportunityName,
                        stage: 'LEAD',
                        status: 'OPEN',
                        probability: 10
                    })
                });
                if (!oppRes.ok) {
                    const err = await oppRes.json().catch(() => ({}));
                    throw new Error(err.detail || 'Failed to create opportunity');
                }
                const opportunity = await oppRes.json();
                finalOppId = opportunity.opportunity_id;
            }

            // 2. Run Analysis
            let res;
            if (activeTab === 'audio') {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('opportunity_id', finalOppId);
                if (email) formData.append('email', email);
                res = await fetch('/api/v1/analyze', {
                    method: 'POST',
                    body: formData
                });
            } else {
                res = await fetch('/api/v1/analyze-text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        opportunity_id: finalOppId,
                        transcript: transcript,
                        email: email || null
                    })
                });
            }

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Interaction processing failed');
            }

            const data = await res.json();
            setResult(data);
            
            // Auto-select the first recommendation if available
            if (data.suggestions && data.suggestions.length > 0) {
                setSelectedRecommendation(0);
                setCustomRecommendation({
                    title: data.suggestions[0].title,
                    action: data.suggestions[0].next_best_action,
                    reason: data.suggestions[0].reasoning,
                    priority: data.suggestions[0].risk_level === 'High' ? 'High' : 'Medium',
                    date: data.suggestions[0].next_reminder_date
                });
            } else {
                setSelectedRecommendation(null);
            }
            
            setStatus('complete');
            if (onComplete) onComplete();
        } catch (err) {
            console.error(err);
            setErrorMessage(err.message || "There was an error processing the interaction. Our engine couldn't extract the insights.");
            setStatus('error');
        } finally {
            setLoading(false);
        }
    };

    const handleSaveAction = async (actionData) => {
        if (!result?.conversation_id) {
            setErrorMessage("Missing conversation context. Please try re-analyzing the interaction.");
            setStatus('error');
            return;
        }
        
        setLoading(true);
        setStatus('uploading'); // Visual feedback that saving is in progress
        
        try {
            const res = await fetch('/api/v1/actions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: result.conversation_id,
                    next_best_action: actionData.title ? `[DECISION: ${actionData.title}] ${actionData.action || 'Follow up'}` : (actionData.action || 'Follow up'),
                    email_generated: actionData.emailDraft || null,
                    task_created: actionData.sendAt || null,
                    send_to: email || null, // Recipient from Step 1
                    deadline: actionData.date,
                    status: 'PENDING'
                })
            });
            
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || "Failed to save the strategic action.");
            }
            
            setStatus('idle');
            onClose();
            if (onComplete) onComplete();
        } catch (err) {
            console.error("Failed to save action", err);
            setErrorMessage(err.message || "Failed to save the decision. Please check your connection and try again.");
            setStatus('error');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay active" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Record New Interaction</h2>
                    <button className="modal-close" onClick={onClose}><X size={20} /></button>
                </div>
                <div className="modal-body">
                    {status === 'idle' && (
                        <form onSubmit={handleSubmit}>
                            <div className="tab-switcher" style={{ display: 'flex', gap: '10px', marginBottom: '20px', background: 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '8px' }}>
                                <button
                                    type="button"
                                    className={`btn ${activeTab === 'audio' ? 'btn-primary' : ''}`}
                                    style={{ flex: 1, fontSize: '0.85rem', padding: '8px' }}
                                    onClick={() => setActiveTab('audio')}
                                >
                                    Audio Call
                                </button>
                                <button
                                    type="button"
                                    className={`btn ${activeTab === 'text' ? 'btn-primary' : ''}`}
                                    style={{ flex: 1, fontSize: '0.85rem', padding: '8px' }}
                                    onClick={() => setActiveTab('text')}
                                >
                                    Text Transcript
                                </button>
                            </div>

                            <div className="detail-grid">
                                <div className="detail-item full-width">
                                    <label className="detail-label">Linked Deal</label>
                                    <select
                                        className="filter-select"
                                        style={{ width: '100%', marginBottom: '15px' }}
                                        value={selectedOpp}
                                        onChange={e => setSelectedOpp(e.target.value)}
                                        required
                                    >
                                        <option value="">-- Select an active opportunity --</option>
                                        <option value="NEW_DEAL" style={{ fontWeight: 'bold', color: 'var(--primary)' }}>+ Create New Opportunity</option>
                                        {opportunities.map(opp => (
                                            <option key={opp.opportunity_id} value={opp.opportunity_id}>
                                                {opp.opportunity_name} ({opp.customer_name})
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {selectedOpp === 'NEW_DEAL' && (
                                    <div className="card" style={{ gridColumn: '1/-1', background: 'rgba(37, 99, 235, 0.1)', border: '1px solid rgba(37, 99, 235, 0.2)', marginBottom: '15px' }}>
                                        <div style={{ padding: '15px' }}>
                                            <h4 style={{ color: 'var(--primary)', marginBottom: '12px', fontSize: '0.9rem' }}>New Customer & Deal Details</h4>
                                            <div className="detail-grid">
                                                <div className="detail-item">
                                                    <label className="detail-label">Customer Name</label>
                                                    <input
                                                        type="text"
                                                        className="filter-select"
                                                        placeholder="Full Name"
                                                        value={newDealData.customerName}
                                                        onChange={e => setNewDealData({ ...newDealData, customerName: e.target.value })}
                                                        required={selectedOpp === 'NEW_DEAL'}
                                                    />
                                                </div>
                                                <div className="detail-item">
                                                    <label className="detail-label">Customer Email</label>
                                                    <input
                                                        type="email"
                                                        className="filter-select"
                                                        placeholder="Email"
                                                        value={newDealData.customerEmail}
                                                        onChange={e => setNewDealData({ ...newDealData, customerEmail: e.target.value })}
                                                        required={selectedOpp === 'NEW_DEAL'}
                                                    />
                                                </div>
                                                <div className="detail-item">
                                                    <label className="detail-label">Company</label>
                                                    <input
                                                        type="text"
                                                        className="filter-select"
                                                        placeholder="Company"
                                                        value={newDealData.company}
                                                        onChange={e => setNewDealData({ ...newDealData, company: e.target.value })}
                                                        required={selectedOpp === 'NEW_DEAL'}
                                                    />
                                                </div>
                                                <div className="detail-item">
                                                    <label className="detail-label">Opp Name</label>
                                                    <input
                                                        type="text"
                                                        className="filter-select"
                                                        placeholder="Deal Name"
                                                        value={newDealData.opportunityName}
                                                        onChange={e => setNewDealData({ ...newDealData, opportunityName: e.target.value })}
                                                        required={selectedOpp === 'NEW_DEAL'}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'audio' ? (
                                    <div className="detail-item full-width">
                                        <label className="detail-label">Upload Recording</label>
                                        <div className="search-box" style={{ padding: '20px', border: '2px dashed var(--border)', display: 'flex', flexDirection: 'column', gap: '10px', textAlign: 'center' }}>
                                            <input
                                                type="file"
                                                accept="audio/*"
                                                onChange={e => setFile(e.target.files[0])}
                                                required={activeTab === 'audio'}
                                            />
                                            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Supported: MP3, WAV, M4A up to 25MB</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="detail-item full-width">
                                        <label className="detail-label">Conversation Transcript</label>
                                        <textarea
                                            className="filter-select"
                                            rows="5"
                                            placeholder="Paste the conversation text here..."
                                            value={transcript}
                                            onChange={e => setTranscript(e.target.value)}
                                            style={{ width: '100%', padding: '12px', height: '120px', backgroundImage: 'none', background: 'rgba(0,0,0,0.2)' }}
                                            required={activeTab === 'text'}
                                        ></textarea>
                                    </div>
                                )}

                                <div className="detail-item full-width" style={{ marginTop: '15px' }}>
                                    <label className="detail-label">Follow-up Email (Optional)</label>
                                    <input
                                        type="email"
                                        className="filter-select"
                                        placeholder="Send AI summary to stakeholder..."
                                        value={email}
                                        onChange={e => setEmail(e.target.value)}
                                        style={{ width: '100%', backgroundImage: 'none', paddingLeft: '16px' }}
                                    />
                                </div>
                            </div>

                            <div style={{ marginTop: '24px' }}>
                                <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '14px', fontWeight: '600' }}>
                                    {activeTab === 'audio' ? <Upload size={18} style={{ marginRight: '8px' }} /> : <CheckCircle2 size={18} style={{ marginRight: '8px' }} />}
                                    Analyze & Update Pipeline
                                </button>
                            </div>
                        </form>
                    )}

                    {status === 'uploading' && (
                        <div className="loading-state" style={{ padding: '40px 0' }}>
                            <Loader2 className="spinner" size={40} />
                            <div>
                                <h3 style={{ marginBottom: '8px' }}>Processing Interaction...</h3>
                                <p style={{ color: 'var(--text-secondary)' }}>
                                    {activeTab === 'audio' ? 'Transcribing audio and extracting AI insights...' : 'Analyzing text and extracting AI insights...'}
                                </p>
                            </div>
                        </div>
                    )}

                    {status === 'complete' && result && (
                        <div style={{ padding: '10px 0' }}>
                            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                                <CheckCircle2 color="var(--success)" size={56} style={{ marginBottom: '16px' }} />
                                <h2 style={{ fontSize: '1.8rem', fontWeight: '800', letterSpacing: '-0.02em' }}>Intelligence Report Ready</h2>
                                <p style={{ color: 'var(--text-secondary)' }}>The interaction analysis is complete. Select your strategy below.</p>
                            </div>

                            <div style={{ textAlign: 'left', marginBottom: '32px' }}>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '10px',
                                    marginBottom: '20px',
                                    padding: '0 4px'
                                }}>
                                    <h3 style={{ fontSize: '1.25rem', fontWeight: '700', margin: 0 }}>Step 1: Choose Your Strategic Strategy</h3>
                                    <div style={{ height: '1px', flex: 1, background: 'linear-gradient(90deg, var(--border), transparent)' }}></div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                    {(result.suggestions || []).slice(0, 3).map((sug, idx) => (
                                        <div
                                            key={idx}
                                            onClick={() => {
                                                setSelectedRecommendation(idx);
                                                try {
                                                    const baseDate = sug.next_reminder_date || new Date().toISOString().split('T')[0];
                                                    const dt = new Date(`${baseDate}T09:00`);
                                                    setSendAt(dt.toISOString().slice(0, 16));
                                                } catch {
                                                    // Fallback to today at 09:00 if parsing fails
                                                    const now = new Date();
                                                    now.setHours(9, 0, 0, 0);
                                                    setSendAt(now.toISOString().slice(0, 16));
                                                }
                                            }}
                                            style={{
                                                position: 'relative',
                                                padding: '20px',
                                                borderRadius: '16px',
                                                background: selectedRecommendation === idx ? 'rgba(37, 99, 235, 0.12)' : 'rgba(255,255,255,0.03)',
                                                border: '2px solid',
                                                borderColor: selectedRecommendation === idx ? 'var(--primary)' : 'rgba(255,255,255,0.08)',
                                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                                cursor: 'pointer',
                                                boxShadow: selectedRecommendation === idx ? '0 8px 32px rgba(37, 99, 235, 0.2)' : 'none'
                                            }}
                                        >
                                            <div style={{
                                                fontWeight: '800',
                                                fontSize: '1.2rem',
                                                color: selectedRecommendation === idx ? 'var(--primary-light)' : '#fff',
                                                marginBottom: '10px',
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'center'
                                            }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                    <span style={{
                                                        width: '24px', height: '24px',
                                                        background: selectedRecommendation === idx ? 'var(--primary)' : 'rgba(255,255,255,0.1)',
                                                        borderRadius: '50%', textAlign: 'center', lineHeight: '24px', fontSize: '0.9rem'
                                                    }}>
                                                        {idx + 1}
                                                    </span>
                                                    <span>{sug.title}</span>
                                                </div>
                                                {selectedRecommendation === idx ? <CheckCircle2 color="var(--primary)" size={22} /> : null}
                                            </div>
                                            <div style={{ color: 'var(--text-secondary)', fontSize: '1rem', lineHeight: '1.6' }}>
                                                <b style={{ color: '#fff', opacity: 0.8 }}>Rationale:</b> {sug.reasoning || sug.next_best_action}
                                            </div>
                                            <div style={{ marginTop: '12px', display: 'flex', gap: '15px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                                <span>📅 {sug.next_reminder_date}</span>
                                                <span style={{ color: sug.risk_level === 'High' ? 'var(--danger)' : (sug.risk_level === 'Medium' ? 'var(--accent)' : 'var(--success)') }}>
                                                    ⚡ {sug.risk_level} Impact
                                                </span>
                                            </div>
                                        </div>
                                    ))}

                                    <div
                                        onClick={() => {
                                            setSelectedRecommendation(null);
                                            // Align sendAt with the custom follow-up date when switching to custom mode
                                            try {
                                                const baseDate = customRecommendation.date || new Date().toISOString().split('T')[0];
                                                const dt = new Date(`${baseDate}T09:00`);
                                                setSendAt(dt.toISOString().slice(0, 16));
                                            } catch {
                                                const now = new Date();
                                                now.setHours(9, 0, 0, 0);
                                                setSendAt(now.toISOString().slice(0, 16));
                                            }
                                        }}
                                        style={{
                                            position: 'relative',
                                            padding: '20px',
                                            borderRadius: '16px',
                                            background: selectedRecommendation === null ? 'rgba(139, 92, 246, 0.1)' : 'rgba(255,255,255,0.02)',
                                            border: '2px solid',
                                            borderColor: selectedRecommendation === null ? 'var(--accent)' : 'rgba(255,255,255,0.08)',
                                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        <div style={{
                                            fontWeight: '800',
                                            fontSize: '1.2rem',
                                            color: selectedRecommendation === null ? 'var(--accent-light)' : 'rgba(255,255,255,0.6)',
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center',
                                            marginBottom: selectedRecommendation === null ? '15px' : '0'
                                        }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <span style={{
                                                    width: '24px', height: '24px',
                                                    background: selectedRecommendation === null ? 'var(--accent)' : 'rgba(255,255,255,0.1)',
                                                    borderRadius: '50%', textAlign: 'center', lineHeight: '24px', fontSize: '1.1rem'
                                                }}>
                                                    +
                                                </span>
                                                <span>Personalized Sales Approach</span>
                                            </div>
                                            {selectedRecommendation === null ? <CheckCircle2 color="var(--accent)" size={22} /> : null}
                                        </div>

                                        {selectedRecommendation === null && (
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '10px' }}>
                                                <div>
                                                    <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Decision Action</label>
                                                    <input
                                                        type="text"
                                                        className="filter-select"
                                                        placeholder="e.g., Send gift hamper"
                                                        style={{ width: '100%', background: 'rgba(0,0,0,0.3)' }}
                                                        value={customRecommendation.action}
                                                        onChange={e => setCustomRecommendation({ ...customRecommendation, action: e.target.value })}
                                                    />
                                                </div>
                                                <div>
                                                    <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Strategic Reason</label>
                                                    <textarea
                                                        className="filter-select"
                                                        placeholder="e.g., Client reached birthday milestone..."
                                                        style={{ width: '100%', background: 'rgba(0,0,0,0.3)', minHeight: '60px' }}
                                                        value={customRecommendation.reason}
                                                        onChange={e => setCustomRecommendation({ ...customRecommendation, reason: e.target.value })}
                                                    />
                                                </div>
                                                <div style={{ display: 'flex', gap: '10px' }}>
                                                    <div style={{ flex: 1 }}>
                                                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Follow-up Date</label>
                                                        <input
                                                            type="date"
                                                            className="filter-select"
                                                            style={{ width: '100%', background: 'rgba(0,0,0,0.3)' }}
                                                            value={customRecommendation.date}
                                                            onChange={e => {
                                                                const value = e.target.value;
                                                                setCustomRecommendation({ ...customRecommendation, date: value });
                                                                // Keep sendAt's date portion in sync when user edits custom date
                                                                if (sendAt) {
                                                                    const timePart = sendAt.split('T')[1] || '09:00';
                                                                    setSendAt(`${value}T${timePart}`);
                                                                } else if (value) {
                                                                    setSendAt(`${value}T09:00`);
                                                                }
                                                            }}
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* New Decision Preview & Email Template Section */}
                            <div style={{
                                marginTop: '24px',
                                marginBottom: '24px',
                                padding: '24px',
                                background: 'rgba(255,255,255,0.03)',
                                border: '1px solid var(--border)',
                                borderRadius: '16px',
                                textAlign: 'left'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                                    <div style={{ width: '4px', height: '20px', background: 'var(--primary)', borderRadius: '2px' }}></div>
                                    <h3 style={{ fontSize: '1.1rem', fontWeight: '700', margin: 0 }}>Strategic Action Preview</h3>
                                </div>
                                <div style={{ marginBottom: '20px' }}>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '8px' }}>Selected Action:</p>
                                    <p style={{ fontWeight: '600', color: '#fff', fontSize: '1.1rem' }}>
                                        {selectedRecommendation !== null
                                            ? result.suggestions[selectedRecommendation].next_best_action
                                            : (customRecommendation.action || "Please describe your custom strategy above...")}
                                    </p>
                                </div>
                                <div>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '8px' }}>Generated Email Template:</p>
                                    <div style={{
                                        background: 'rgba(0,0,0,0.3)',
                                        padding: '16px',
                                        borderRadius: '12px',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        fontSize: '0.9rem',
                                        lineHeight: '1.6',
                                        color: '#cbd5e1',
                                        whiteSpace: 'pre-wrap',
                                        maxHeight: '200px',
                                        overflowY: 'auto'
                                    }}>
                                        {selectedRecommendation !== null
                                            ? (result.suggestions[selectedRecommendation].email_draft || "No specific draft generated.")
                                            : "A personalized follow-up email will be prepared based on your custom strategy."}
                                    </div>
                                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                                        * This draft will be used for the follow-up if an email address was provided in Step 1.
                                    </p>
                                </div>

                                <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                        Target send date &amp; time
                                    </label>
                                    <input
                                        type="datetime-local"
                                        className="filter-select"
                                        style={{ maxWidth: '260px', background: 'rgba(0,0,0,0.3)' }}
                                        value={sendAt}
                                        onChange={e => setSendAt(e.target.value)}
                                    />
                                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        This is when you plan to send / follow up. The action deadline will be stored accordingly.
                                    </p>
                                </div>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                <button
                                    className="btn btn-primary"
                                    style={{
                                        width: '100%',
                                        padding: '18px',
                                        fontSize: '1.2rem',
                                        fontWeight: '800',
                                        background: 'linear-gradient(135deg, var(--primary), #1d4ed8)',
                                        border: 'none',
                                        borderRadius: '14px',
                                        boxShadow: '0 8px 32px rgba(37, 99, 235, 0.4)'
                                    }}
                                    onClick={() => {
                                        if (selectedRecommendation !== null) {
                                            const sug = result.suggestions[selectedRecommendation];
                                            handleSaveAction({
                                                title: sug.title,
                                                action: sug.next_best_action,
                                                date: sendAt ? sendAt.split('T')[0] : sug.next_reminder_date,
                                                emailDraft: sug.email_draft,
                                                sendAt
                                            });
                                        } else {
                                            handleSaveAction({
                                                ...customRecommendation,
                                                title: 'Custom Decision',
                                                emailDraft: null,
                                                sendAt
                                            });
                                        }
                                    }}
                                >
                                    CONFIRM STRATEGIC ACTION
                                </button>

                                <div style={{ height: '1px', background: 'var(--border)', margin: '16px 0' }}></div>

                                <div style={{ textAlign: 'center' }}>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
                                        Alternatively, if the deal has reached its final state based on this interaction:
                                    </p>
                                    <div style={{ display: 'flex', gap: '12px' }}>
                                        <button
                                            className="btn"
                                            style={{
                                                flex: 1,
                                                padding: '14px',
                                                background: 'rgba(34, 197, 94, 0.1)',
                                                color: '#4ade80',
                                                border: '1px solid rgba(34, 197, 94, 0.3)',
                                                fontWeight: '700'
                                            }}
                                            onClick={async () => {
                                                if (confirm("Close this deal as WON?")) {
                                                    await fetch(`/api/v1/opportunities/${selectedOpp}`, {
                                                        method: 'PUT',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ status: 'CLOSED_WON', closed_date: new Date().toISOString().split('T')[0] })
                                                    });
                                                    onClose();
                                                    if (onComplete) onComplete();
                                                }
                                            }}
                                        >
                                            ✅ CLOSED WON
                                        </button>
                                        <button
                                            className="btn"
                                            style={{
                                                flex: 1,
                                                padding: '14px',
                                                background: 'rgba(239, 68, 68, 0.1)',
                                                color: '#f87171',
                                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                                fontWeight: '700'
                                            }}
                                            onClick={async () => {
                                                if (confirm("Close this deal as LOST?")) {
                                                    await fetch(`/api/v1/opportunities/${selectedOpp}`, {
                                                        method: 'PUT',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ status: 'CLOSED_LOST', closed_date: new Date().toISOString().split('T')[0] })
                                                    });
                                                    onClose();
                                                    if (onComplete) onComplete();
                                                }
                                            }}
                                        >
                                            ❌ CLOSED LOST
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {status === 'error' && (
                        <div style={{ textAlign: 'center', padding: '60px 0' }}>
                            <div style={{
                                width: '80px',
                                height: '80px',
                                borderRadius: '50%',
                                background: 'rgba(239, 68, 68, 0.1)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                margin: '0 auto 24px'
                            }}>
                                <AlertCircle color="var(--danger)" size={48} />
                            </div>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '12px' }}>Analysis Failed</h2>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '400px', margin: '0 auto 32px' }}>
                                {errorMessage}
                            </p>
                            <button
                                className="btn btn-secondary"
                                style={{ padding: '12px 32px', fontWeight: '600' }}
                                onClick={() => setStatus('idle')}
                            >
                                Try Again
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
