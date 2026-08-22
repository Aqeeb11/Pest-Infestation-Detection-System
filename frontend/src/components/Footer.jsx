import { Link } from 'react-router-dom'

function Footer() {
  return <footer className="site-footer"><div className="site-footer-inner"><span>© GrapeGuard AI · Intelligent grape health</span><span><Link to="/help">Help</Link><Link to="/about">About</Link></span></div></footer>
}

export default Footer
