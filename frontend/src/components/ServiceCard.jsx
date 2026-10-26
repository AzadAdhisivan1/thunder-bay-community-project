// Owner: Kamakshi (US-02, US-03).
// One result in the list: name, category, address, and a link to /services/<id>.
export default function ServiceCard({ service }) {
  return <article className="service-card">{service?.name}</article>
}
