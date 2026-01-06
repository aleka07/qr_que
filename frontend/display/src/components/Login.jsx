import React, { useState } from 'react';
import './Login.css';

function Login({ onLogin, error }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username || !password) return;

        setLoading(true);
        try {
            await onLogin(username, password);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <div className="login-header">
                    <div className="login-logo">📺</div>
                    <h1>QR Queue Display</h1>
                    <p>Авторизация планшета</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="username">Логин</label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Введите логин"
                            autoComplete="username"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Введите пароль"
                            autoComplete="current-password"
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="login-button"
                        disabled={loading || !username || !password}
                    >
                        {loading ? 'Вход...' : 'Войти'}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default Login;
