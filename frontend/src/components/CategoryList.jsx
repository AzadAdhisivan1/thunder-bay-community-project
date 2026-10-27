// Owner: Kamakshi (US-02).
// Loads getCategories() and links each one to /results?category=<slug>.
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCategories } from '../api/client.js'

export default function CategoryList() {
  const [categories, setCategories] = useState([])
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    let ignore = false
    getCategories()
      .then((data) => {
        if (!ignore) {
          setCategories(data)
          setStatus('done')
        }
      })
      .catch(() => {
        if (!ignore) setStatus('error')
      })
    return () => {
      ignore = true
    }
  }, [])

  return (
    <section className="category-list" id="categories" aria-labelledby="categories-heading">
      <h2 id="categories-heading">Browse by category</h2>
      {status === 'loading' && <p className="status">Loading categories...</p>}
      {status === 'error' && (
        <p className="status status-error" role="alert">
          Could not load categories. Please try again later.
        </p>
      )}
      {status === 'done' && categories.length === 0 && (
        <p className="status">No categories yet.</p>
      )}
      {status === 'done' && categories.length > 0 && (
        <ul className="category-grid">
          {categories.map((category) => (
            <li key={category.id}>
              <Link
                className="category-link"
                to={`/results?category=${encodeURIComponent(category.slug)}`}
              >
                {category.name}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
