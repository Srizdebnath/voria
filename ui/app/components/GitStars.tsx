'use client';

import { useEffect, useState } from 'react';

interface GitStarsProps {}

export function GitStars() {
  const [stars, setStars] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://api.github.com/repos/Srizdebnath/voria', {
      headers: {
        Accept: 'application/vnd.github.v3+json',
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setStars(data.stargazers_count || 0);
        setLoading(false);
      })
      .catch(() => {
        setStars(0);
        setLoading(false);
      });
  }, []);

  return (
    <div className="brutal-box" style={{ textAlign: 'center', background: '#00ff88' }}>
      <p style={{ fontSize: '1rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>⭐ GitHub Stars</p>
      {loading ? (
        <p className="stars-counter">...</p>
      ) : (
        <>
          <p className="stars-counter">{stars}</p>
          <a
            href="https://github.com/Srizdebnath/voria"
            target="_blank"
            rel="noopener noreferrer"
            className="brutal-btn"
            style={{ marginTop: '1rem', background: '#ff6b35' }}
          >
            ⭐ Star Us on GitHub
          </a>
        </>
      )}
    </div>
  );
}