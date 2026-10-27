// Owner: Kamakshi (US-03).
// Text box + search button. Empty input is not sent; ask the user to type something.
// On submit, go to /results?q=<text>.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SearchBar({ initialQuery = '' }) {
  const [query, setQuery] = useState(initialQuery)
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

  function handleSubmit(event) {
    event.preventDefault()
    const text = query.trim()
    if (!text) {
      setMessage('Please type something to search')
      return
    }
    setMessage('')
    navigate(`/results?q=${encodeURIComponent(text)}`)
  }

  return (
    <form className="search-bar" role="search" onSubmit={handleSubmit} noValidate>
      <label htmlFor="search-input">Search for a service</label>
      <div className="search-row">
        <input
          id="search-input"
          type="search"
          value={query}
          placeholder="e.g. food bank, shelter"
          onChange={(event) => {
            setQuery(event.target.value)
            if (message) setMessage('')
          }}
          aria-describedby={message ? 'search-message' : undefined}
        />
        <button type="submit">Search</button>
      </div>
      {message && (
        <p id="search-message" className="status status-error" role="alert">
          {message}
        </p>
      )}
    </form>
  )
}
