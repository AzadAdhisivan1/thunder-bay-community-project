import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getServicesByCategory, searchServices } from '../api/client.js'
import ResultsMap from '../components/ResultsMap.jsx'
import SearchBar from '../components/SearchBar.jsx'
import ServiceCard from '../components/ServiceCard.jsx'

// Owner: Kamakshi (list, US-02/03) + Dhara (map, US-05).
// Reads ?category=<slug> or ?q=<text> from the URL, loads results from api/client.js,
// shows them as ServiceCards and passes the same list to ResultsMap.
export default function ResultsPage() {
  const [searchParams] = useSearchParams()
  const query = (searchParams.get('q') || '').trim()
  const category = (searchParams.get('category') || '').trim()

  const [services, setServices] = useState([])
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    if (!query && !category) {
      setServices([])
      setStatus('idle')
      return undefined
    }

    let ignore = false
    setStatus('loading')
    setServices([])
    const load = query ? searchServices(query) : getServicesByCategory(category)
    load
      .then((data) => {
        if (!ignore) {
          setServices(data)
          setStatus('done')
        }
      })
      .catch(() => {
        if (!ignore) setStatus('error')
      })
    return () => {
      ignore = true
    }
  }, [query, category])

  // The category name comes from the results; fall back to the slug before they load.
  const categoryName = services[0]?.category?.name || category
  let heading = 'Results'
  if (query) heading = `Results for "${query}"`
  else if (category) heading = `Category: ${categoryName}`

  return (
    <section className="results-page">
      <h1>{heading}</h1>
      <SearchBar key={query} initialQuery={query} />

      {status === 'idle' && (
        <p className="status">
          Type a search above or <Link to="/#categories">browse the categories</Link>.
        </p>
      )}
      {status === 'loading' && <p className="status">Loading results...</p>}
      {status === 'error' && (
        <p className="status status-error" role="alert">
          Could not load results. Please try again later.
        </p>
      )}
      {status === 'done' && services.length === 0 && (
        <p className="status">
          No results found. <Link to="/#categories">Browse the categories</Link> instead.
        </p>
      )}

      {status === 'done' && services.length > 0 && (
        <div className="results-layout">
          <ul className="results-list" aria-label="Results list">
            {services.map((service) => (
              <li key={service.id}>
                <ServiceCard service={service} />
              </li>
            ))}
          </ul>
          <div className="results-map-wrap">
            <ResultsMap services={services} />
          </div>
        </div>
      )}
    </section>
  )
}
