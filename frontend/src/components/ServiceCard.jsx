// Owner: Kamakshi (US-02, US-03).
// One result in the list: name, category, address, and a link to /services/<id>.
import { Link } from 'react-router-dom'

export default function ServiceCard({ service }) {
  return (
    <article className="service-card">
      <h3 className="service-card-name">{service.name}</h3>
      {service.category?.name && <p className="service-card-category">{service.category.name}</p>}
      <p className="service-card-address">{service.address || 'Address not available'}</p>
      <Link className="service-card-link" to={`/services/${service.id}`}>
        View details<span className="visually-hidden"> for {service.name}</span>
      </Link>
    </article>
  )
}
