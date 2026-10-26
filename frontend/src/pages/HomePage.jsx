import CategoryList from '../components/CategoryList.jsx'
import SearchBar from '../components/SearchBar.jsx'

// Owner: Kamakshi (US-02, US-03). Home page with the search bar and category list.
export default function HomePage() {
  return (
    <section>
      <h1>Find community services in Thunder Bay</h1>
      <SearchBar />
      <CategoryList />
    </section>
  )
}
