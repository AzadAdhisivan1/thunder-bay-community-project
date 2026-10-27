import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getService } from '../api/client.js'

// Owner: Kamakshi (US-04).
// Shows name, address, hours, phone, website and eligibility.
// Missing fields say "Not available"; a removed service shows "Service not found".
const NOT_AVAILABLE = 'Not available'

function hasValue(value) {
  return value !== null && value !== undefined && String(value).trim() !== ''
}

// Only http(s) addresses become links, so a bad value can't run script.
function isWebLink(value) {
  return hasValue(value) && /^https?:\/\//i.test(value.trim())
}

function Field({ label, children }) {
  return (
    <div className="detail-row">
      <dt>{label}</dt>
      <dd>{children}</dd>
    </div>
  )
}

export default function ServiceDetailsPage() {
  const { id } = useParams()
  const [service, setService] = useState(null)
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    let ignore = false
    setStatus('loading')
    setService(null)
    getService(id)
      .then((data) => {
        if (!ignore) {
          setService(data)
          setStatus('done')
        }
      })
      .catch((error) => {
        if (!ignore) setStatus(error?.status === 404 ? 'not-found' : 'error')
      })
    return () => {
      ignore = true
    }
  }, [id])

  if (status === 'loading') {
    return (
      <section className="details-page">
        <p className="status">Loading service...</p>
      </section>
    )
  }

  if (status === 'not-found' || status === 'error') {
    return (
      <section className="details-page">
        <h1>{status === 'not-found' ? 'Service not found' : 'Something went wrong'}</h1>
        <p className="status" role="alert">
          {status === 'not-found'
            ? 'This service may have been removed.'
            : 'Could not load this service. Please try again later.'}
        </p>
        <Link to="/#categories">Back to categories</Link>
      </section>
    )
  }

  const text = (value) => (hasValue(value) ? value : NOT_AVAILABLE)

  return (
    <section className="details-page">
      <h1>{text(service.name)}</h1>
      <dl className="details-list">
        <Field label="Category">{text(service.category?.name)}</Field>
        <Field label="Address">{text(service.address)}</Field>
        <Field label="Hours">{text(service.hours)}</Field>
        <Field label="Phone">
          {hasValue(service.phone) ? (
            <a href={`tel:${service.phone.replace(/[^\d+]/g, '')}`}>{service.phone}</a>
          ) : (
            NOT_AVAILABLE
          )}
        </Field>
        <Field label="Website">
          {isWebLink(service.website) ? (
            <a href={service.website} target="_blank" rel="noopener noreferrer">
              {service.website}
            </a>
          ) : (
            text(service.website)
          )}
        </Field>
        <Field label="Eligibility">{text(service.eligibility)}</Field>
      </dl>
      <Link to="/#categories">Back to categories</Link>
    </section>
  )
}
