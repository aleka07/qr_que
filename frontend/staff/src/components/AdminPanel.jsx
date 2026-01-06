import React, { useState, useEffect } from 'react';
import {
    getUsers,
    createUser,
    updateUser,
    resetUserPassword,
    getLocations,
    getOrganizations,
    createOrganization,
    updateOrganization,
    createLocation,
    updateLocation,
} from '../api';
import './AdminPanel.css';

const ROLES = [
    { value: 'admin', label: 'Администратор', description: 'Полный доступ' },
    { value: 'owner', label: 'Владелец', description: 'Все точки организации' },
    { value: 'manager', label: 'Менеджер', description: 'Своя точка' },
    { value: 'staff', label: 'Персонал', description: 'Только заказы' },
];

function AdminPanel({ currentUser }) {
    const [activeTab, setActiveTab] = useState('users');
    const [users, setUsers] = useState([]);
    const [organizations, setOrganizations] = useState([]);
    const [locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [userSearch, setUserSearch] = useState('');

    // User form state
    const [showUserForm, setShowUserForm] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [userFormData, setUserFormData] = useState({
        username: '', email: '', full_name: '', password: '',
        role: 'staff', organization_id: '', location_id: '', is_active: true,
    });

    // Organization form state
    const [showOrgForm, setShowOrgForm] = useState(false);
    const [editingOrg, setEditingOrg] = useState(null);
    const [orgFormData, setOrgFormData] = useState({
        name: '', slug: '', is_active: true,
    });

    // Location form state
    const [showLocForm, setShowLocForm] = useState(false);
    const [editingLoc, setEditingLoc] = useState(null);
    const [locFormData, setLocFormData] = useState({
        name: '', slug: '', organization_id: '', mall_name: '', city: '', address: '', is_active: true,
    });

    // Password reset
    const [showPasswordReset, setShowPasswordReset] = useState(null);
    const [newPassword, setNewPassword] = useState('');

    useEffect(() => { loadData(); }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [usersData, orgsData, locsData] = await Promise.all([
                getUsers(), getOrganizations(), getLocations(),
            ]);
            setUsers(usersData);
            setOrganizations(orgsData);
            setLocations(locsData);
        } catch (err) {
            setError('Ошибка загрузки данных');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const showMessage = (msg, isError = false) => {
        if (isError) setError(msg); else setSuccess(msg);
        setTimeout(() => { setError(null); setSuccess(null); }, 3000);
    };

    // ==================== USER HANDLERS ====================
    const handleUserSubmit = async (e) => {
        e.preventDefault();
        try {
            const userData = {
                ...userFormData,
                organization_id: userFormData.organization_id || null,
                location_id: userFormData.location_id || null,
            };
            if (editingUser && !userData.password) delete userData.password;

            if (editingUser) {
                await updateUser(editingUser.id, userData);
                showMessage('Пользователь обновлён');
            } else {
                await createUser(userData);
                showMessage('Пользователь создан');
            }
            setShowUserForm(false);
            setEditingUser(null);
            loadData();
        } catch (err) {
            showMessage(err.message, true);
        }
    };

    const handleEditUser = (user) => {
        setEditingUser(user);
        setUserFormData({
            username: user.username, email: user.email || '', full_name: user.full_name || '',
            password: '', role: user.role, organization_id: user.organization_id || '',
            location_id: user.location_id || '', is_active: user.is_active,
        });
        setShowUserForm(true);
    };

    const handleNewUser = () => {
        setEditingUser(null);
        setUserFormData({
            username: '', email: '', full_name: '', password: '', role: 'staff',
            organization_id: currentUser?.organization_id || '', location_id: '', is_active: true,
        });
        setShowUserForm(true);
    };

    const handleResetPassword = async () => {
        if (!newPassword || newPassword.length < 6) {
            showMessage('Пароль должен быть минимум 6 символов', true);
            return;
        }
        try {
            await resetUserPassword(showPasswordReset, newPassword);
            showMessage('Пароль сброшен');
            setShowPasswordReset(null);
            setNewPassword('');
        } catch (err) {
            showMessage(err.message, true);
        }
    };

    // ==================== ORGANIZATION HANDLERS ====================
    const handleOrgSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingOrg) {
                await updateOrganization(editingOrg.id, orgFormData);
                showMessage('Организация обновлена');
            } else {
                await createOrganization(orgFormData);
                showMessage('Организация создана');
            }
            setShowOrgForm(false);
            setEditingOrg(null);
            loadData();
        } catch (err) {
            showMessage(err.message, true);
        }
    };

    const handleEditOrg = (org) => {
        setEditingOrg(org);
        setOrgFormData({ name: org.name, slug: org.slug, is_active: org.is_active });
        setShowOrgForm(true);
    };

    const handleNewOrg = () => {
        setEditingOrg(null);
        setOrgFormData({ name: '', slug: '', is_active: true });
        setShowOrgForm(true);
    };

    // ==================== LOCATION HANDLERS ====================
    const handleLocSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingLoc) {
                await updateLocation(editingLoc.id, locFormData);
                showMessage('Локация обновлена');
            } else {
                await createLocation(locFormData);
                showMessage('Локация создана');
            }
            setShowLocForm(false);
            setEditingLoc(null);
            loadData();
        } catch (err) {
            showMessage(err.message, true);
        }
    };

    const handleEditLoc = (loc) => {
        setEditingLoc(loc);
        setLocFormData({
            name: loc.name, slug: loc.slug, organization_id: loc.organization_id,
            mall_name: loc.mall_name || '', city: loc.city || '', address: loc.address || '', is_active: loc.is_active,
        });
        setShowLocForm(true);
    };

    const handleNewLoc = () => {
        setEditingLoc(null);
        setLocFormData({
            name: '', slug: '', organization_id: currentUser?.organization_id || (organizations[0]?.id || ''),
            mall_name: '', city: '', address: '', is_active: true,
        });
        setShowLocForm(true);
    };

    // ==================== HELPERS ====================
    const getRoleBadgeClass = (role) => ({ admin: 'role-admin', owner: 'role-owner', manager: 'role-manager', staff: 'role-staff' }[role] || '');
    const getRoleLabel = (role) => ROLES.find(r => r.value === role)?.label || role;
    const filteredLocations = userFormData.organization_id ? locations.filter(l => l.organization_id === userFormData.organization_id) : locations;

    // Filter users by search
    const filteredUsers = users.filter(user => {
        if (!userSearch.trim()) return true;
        const search = userSearch.toLowerCase();
        return (
            user.username?.toLowerCase().includes(search) ||
            user.full_name?.toLowerCase().includes(search) ||
            user.email?.toLowerCase().includes(search) ||
            user.organization_name?.toLowerCase().includes(search) ||
            user.location_name?.toLowerCase().includes(search)
        );
    });

    if (loading) return <div className="admin-panel loading">Загрузка...</div>;

    return (
        <div className="admin-panel">
            {/* Tab Navigation */}
            <div className="admin-tabs">
                <button className={`admin-tab ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
                    👥 Пользователи
                </button>
                {currentUser?.role === 'admin' && (
                    <>
                        <button className={`admin-tab ${activeTab === 'organizations' ? 'active' : ''}`} onClick={() => setActiveTab('organizations')}>
                            🏢 Организации
                        </button>
                        <button className={`admin-tab ${activeTab === 'locations' ? 'active' : ''}`} onClick={() => setActiveTab('locations')}>
                            📍 Локации
                        </button>
                    </>
                )}
                {currentUser?.role === 'owner' && (
                    <button className={`admin-tab ${activeTab === 'locations' ? 'active' : ''}`} onClick={() => setActiveTab('locations')}>
                        📍 Локации
                    </button>
                )}
            </div>

            {error && <div className="admin-error">{error}</div>}
            {success && <div className="admin-success">{success}</div>}

            {/* ==================== USERS TAB ==================== */}
            {activeTab === 'users' && (
                <>
                    <div className="admin-header">
                        <h2>👥 Пользователи ({filteredUsers.length})</h2>
                        <div className="header-actions">
                            <input
                                type="text"
                                className="search-input"
                                placeholder="🔍 Поиск..."
                                value={userSearch}
                                onChange={e => setUserSearch(e.target.value)}
                            />
                            <button className="btn-primary" onClick={handleNewUser}>+ Новый</button>
                        </div>
                    </div>
                    <div className="users-table-container">
                        <table className="users-table">
                            <thead>
                                <tr><th>Пользователь</th><th>Роль</th><th>Организация</th><th>Локация</th><th>Статус</th><th>Действия</th></tr>
                            </thead>
                            <tbody>
                                {filteredUsers.map(user => (
                                    <tr key={user.id} className={!user.is_active ? 'inactive' : ''}>
                                        <td><div className="user-cell"><strong>{user.full_name || user.username}</strong><span className="username">@{user.username}</span></div></td>
                                        <td><span className={`role-badge ${getRoleBadgeClass(user.role)}`}>{getRoleLabel(user.role)}</span></td>
                                        <td>{user.organization_name || '—'}</td>
                                        <td>{user.location_name || '—'}</td>
                                        <td><span className={`status-badge ${user.is_active ? 'active' : 'blocked'}`}>{user.is_active ? 'Активен' : 'Заблокирован'}</span></td>
                                        <td>
                                            <div className="action-buttons">
                                                <button className="btn-icon" onClick={() => handleEditUser(user)} title="Редактировать">✏️</button>
                                                <button className="btn-icon" onClick={() => setShowPasswordReset(user.id)} title="Сбросить пароль">🔑</button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}

            {/* ==================== ORGANIZATIONS TAB ==================== */}
            {activeTab === 'organizations' && (
                <>
                    <div className="admin-header">
                        <h2>🏢 Организации</h2>
                        <button className="btn-primary" onClick={handleNewOrg}>+ Новая</button>
                    </div>
                    <div className="users-table-container">
                        <table className="users-table">
                            <thead><tr><th>Название</th><th>Slug</th><th>Локации</th><th>Статус</th><th>Действия</th></tr></thead>
                            <tbody>
                                {organizations.map(org => (
                                    <tr key={org.id} className={!org.is_active ? 'inactive' : ''}>
                                        <td><strong>{org.name}</strong></td>
                                        <td><code>{org.slug}</code></td>
                                        <td>{org.locations?.length || 0}</td>
                                        <td><span className={`status-badge ${org.is_active ? 'active' : 'blocked'}`}>{org.is_active ? 'Активна' : 'Неактивна'}</span></td>
                                        <td><button className="btn-icon" onClick={() => handleEditOrg(org)} title="Редактировать">✏️</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}

            {/* ==================== LOCATIONS TAB ==================== */}
            {activeTab === 'locations' && (
                <>
                    <div className="admin-header">
                        <h2>📍 Локации</h2>
                        <button className="btn-primary" onClick={handleNewLoc}>+ Новая</button>
                    </div>
                    <div className="users-table-container">
                        <table className="users-table">
                            <thead><tr><th>Название</th><th>Организация</th><th>ТРЦ</th><th>Город</th><th>Статус</th><th>Действия</th></tr></thead>
                            <tbody>
                                {locations.map(loc => (
                                    <tr key={loc.id} className={!loc.is_active ? 'inactive' : ''}>
                                        <td><strong>{loc.name}</strong></td>
                                        <td>{loc.organization_name || organizations.find(o => o.id === loc.organization_id)?.name || '—'}</td>
                                        <td>{loc.mall_name || '—'}</td>
                                        <td>{loc.city || '—'}</td>
                                        <td><span className={`status-badge ${loc.is_active ? 'active' : 'blocked'}`}>{loc.is_active ? 'Активна' : 'Неактивна'}</span></td>
                                        <td><button className="btn-icon" onClick={() => handleEditLoc(loc)} title="Редактировать">✏️</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}

            {/* ==================== USER FORM MODAL ==================== */}
            {showUserForm && (
                <div className="modal-overlay" onClick={() => setShowUserForm(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingUser ? 'Редактирование' : 'Новый пользователь'}</h3>
                            <button className="modal-close" onClick={() => setShowUserForm(false)}>×</button>
                        </div>
                        <form onSubmit={handleUserSubmit} className="user-form">
                            <div className="form-row">
                                <div className="form-group"><label>Логин *</label><input type="text" value={userFormData.username} onChange={e => setUserFormData({ ...userFormData, username: e.target.value })} required disabled={editingUser} /></div>
                                <div className="form-group"><label>Email</label><input type="email" value={userFormData.email} onChange={e => setUserFormData({ ...userFormData, email: e.target.value })} /></div>
                            </div>
                            <div className="form-row">
                                <div className="form-group"><label>Полное имя</label><input type="text" value={userFormData.full_name} onChange={e => setUserFormData({ ...userFormData, full_name: e.target.value })} /></div>
                                <div className="form-group"><label>{editingUser ? 'Новый пароль' : 'Пароль *'}</label><input type="password" value={userFormData.password} onChange={e => setUserFormData({ ...userFormData, password: e.target.value })} required={!editingUser} placeholder={editingUser ? 'Оставьте пустым' : ''} /></div>
                            </div>
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Роль *</label>
                                    <select value={userFormData.role} onChange={e => setUserFormData({ ...userFormData, role: e.target.value })}>
                                        {ROLES.filter(r => currentUser?.role === 'admin' || r.value !== 'admin').map(role => (
                                            <option key={role.value} value={role.value}>{role.label} — {role.description}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Статус</label>
                                    <select value={userFormData.is_active ? 'active' : 'inactive'} onChange={e => setUserFormData({ ...userFormData, is_active: e.target.value === 'active' })}>
                                        <option value="active">Активен</option>
                                        <option value="inactive">Заблокирован</option>
                                    </select>
                                </div>
                            </div>
                            {currentUser?.role === 'admin' && (
                                <div className="form-group">
                                    <label>Организация</label>
                                    <select value={userFormData.organization_id} onChange={e => setUserFormData({ ...userFormData, organization_id: e.target.value, location_id: '' })}>
                                        <option value="">— Не выбрана —</option>
                                        {organizations.map(org => <option key={org.id} value={org.id}>{org.name}</option>)}
                                    </select>
                                </div>
                            )}
                            {(userFormData.role === 'manager' || userFormData.role === 'staff') && (
                                <div className="form-group">
                                    <label>Локация *</label>
                                    <select value={userFormData.location_id} onChange={e => setUserFormData({ ...userFormData, location_id: e.target.value })} required>
                                        <option value="">— Выберите локацию —</option>
                                        {filteredLocations.map(loc => <option key={loc.id} value={loc.id}>{loc.name} {loc.mall_name ? `(${loc.mall_name})` : ''}</option>)}
                                    </select>
                                </div>
                            )}
                            <div className="form-actions">
                                <button type="button" className="btn-secondary" onClick={() => setShowUserForm(false)}>Отмена</button>
                                <button type="submit" className="btn-primary">{editingUser ? 'Сохранить' : 'Создать'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* ==================== ORGANIZATION FORM MODAL ==================== */}
            {showOrgForm && (
                <div className="modal-overlay" onClick={() => setShowOrgForm(false)}>
                    <div className="modal modal-small" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingOrg ? 'Редактирование организации' : 'Новая организация'}</h3>
                            <button className="modal-close" onClick={() => setShowOrgForm(false)}>×</button>
                        </div>
                        <form onSubmit={handleOrgSubmit} className="user-form">
                            <div className="form-group"><label>Название *</label><input type="text" value={orgFormData.name} onChange={e => setOrgFormData({ ...orgFormData, name: e.target.value })} required /></div>
                            <div className="form-group"><label>Slug (URL) *</label><input type="text" value={orgFormData.slug} onChange={e => setOrgFormData({ ...orgFormData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '') })} required placeholder="например: kfc" /></div>
                            <div className="form-group">
                                <label>Статус</label>
                                <select value={orgFormData.is_active ? 'active' : 'inactive'} onChange={e => setOrgFormData({ ...orgFormData, is_active: e.target.value === 'active' })}>
                                    <option value="active">Активна</option>
                                    <option value="inactive">Неактивна</option>
                                </select>
                            </div>
                            <div className="form-actions">
                                <button type="button" className="btn-secondary" onClick={() => setShowOrgForm(false)}>Отмена</button>
                                <button type="submit" className="btn-primary">{editingOrg ? 'Сохранить' : 'Создать'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* ==================== LOCATION FORM MODAL ==================== */}
            {showLocForm && (
                <div className="modal-overlay" onClick={() => setShowLocForm(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingLoc ? 'Редактирование локации' : 'Новая локация'}</h3>
                            <button className="modal-close" onClick={() => setShowLocForm(false)}>×</button>
                        </div>
                        <form onSubmit={handleLocSubmit} className="user-form">
                            <div className="form-row">
                                <div className="form-group"><label>Название *</label><input type="text" value={locFormData.name} onChange={e => setLocFormData({ ...locFormData, name: e.target.value })} required /></div>
                                <div className="form-group"><label>Slug (URL) *</label><input type="text" value={locFormData.slug} onChange={e => setLocFormData({ ...locFormData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '') })} required placeholder="например: mega-almaty" /></div>
                            </div>
                            {currentUser?.role === 'admin' && (
                                <div className="form-group">
                                    <label>Организация *</label>
                                    <select value={locFormData.organization_id} onChange={e => setLocFormData({ ...locFormData, organization_id: e.target.value })} required>
                                        <option value="">— Выберите —</option>
                                        {organizations.map(org => <option key={org.id} value={org.id}>{org.name}</option>)}
                                    </select>
                                </div>
                            )}
                            <div className="form-row">
                                <div className="form-group"><label>ТРЦ / Молл</label><input type="text" value={locFormData.mall_name} onChange={e => setLocFormData({ ...locFormData, mall_name: e.target.value })} placeholder="например: Mega Almaty" /></div>
                                <div className="form-group"><label>Город</label><input type="text" value={locFormData.city} onChange={e => setLocFormData({ ...locFormData, city: e.target.value })} placeholder="например: Алматы" /></div>
                            </div>
                            <div className="form-group"><label>Адрес</label><input type="text" value={locFormData.address} onChange={e => setLocFormData({ ...locFormData, address: e.target.value })} placeholder="Полный адрес" /></div>
                            <div className="form-group">
                                <label>Статус</label>
                                <select value={locFormData.is_active ? 'active' : 'inactive'} onChange={e => setLocFormData({ ...locFormData, is_active: e.target.value === 'active' })}>
                                    <option value="active">Активна</option>
                                    <option value="inactive">Неактивна</option>
                                </select>
                            </div>
                            <div className="form-actions">
                                <button type="button" className="btn-secondary" onClick={() => setShowLocForm(false)}>Отмена</button>
                                <button type="submit" className="btn-primary">{editingLoc ? 'Сохранить' : 'Создать'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* ==================== PASSWORD RESET MODAL ==================== */}
            {showPasswordReset && (
                <div className="modal-overlay" onClick={() => setShowPasswordReset(null)}>
                    <div className="modal modal-small" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Сброс пароля</h3>
                            <button className="modal-close" onClick={() => setShowPasswordReset(null)}>×</button>
                        </div>
                        <div className="password-reset-form">
                            <div className="form-group"><label>Новый пароль</label><input type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="Минимум 6 символов" /></div>
                            <div className="form-actions">
                                <button className="btn-secondary" onClick={() => setShowPasswordReset(null)}>Отмена</button>
                                <button className="btn-primary" onClick={handleResetPassword}>Сбросить</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default AdminPanel;
