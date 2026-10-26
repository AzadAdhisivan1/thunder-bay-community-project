import ResultsMap from '../components/ResultsMap.jsx'

// Owner: Kamakshi (list, US-02/03) + Dhara (map, US-05).
// Reads ?category=<slug> or ?q=<text> from the URL, loads results from api/client.js,
// shows them as ServiceCards and passes the same list to ResultsMap.
export default function ResultsPage() {
  return (
    <section>
      <h1>Results</h1>
      <p>TODO (US-02, US-03): load and list results here.</p>
      <ResultsMap services={[]} />
    </section>
  )
}
