import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Link } from 'react-router-dom';

function CategoryList() {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    api.get('categories/')  // NO headers here, public access
      .then(res => setCategories(res.data))
      .catch(err => console.error("API error:", err));
  }, []);

  return (
    <div>
      <h1>Categories</h1>
      <ul>
        {categories.map(cat => (
          <li key={cat.id}>
            <Link to={`/category/${cat.id}`}>{cat.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CategoryList;
