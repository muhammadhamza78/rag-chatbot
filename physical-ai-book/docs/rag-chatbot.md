---
title: RAG Chatbot
---

import React, { useState } from 'react';

# RAG Chatbot Demo

<Chatbot />

export function Chatbot() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const ask = async () => {
    const res = await fetch('http://127.0.0.1:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    setAnswer(data.answer);
  };

  return (
    <div>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder='Ask something...'
        style={{ padding: '8px', width: '300px', marginRight: '8px' }}
      />
      <button onClick={ask} style={{ padding: '8px' }}>Ask</button>
      <p>{answer}</p>
    </div>
  );
}
