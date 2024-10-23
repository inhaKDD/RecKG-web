import React from 'react';
import { Link } from 'react-router-dom';


const NavBar: React.FC = () => {
	return (
		<nav className="sticky top-0 flex gap-4 p-4">
			<div className="font-black">
				<Link to="/">RecKG</Link>
			</div>
			<ul className="navbar-links flex gap-2">
				<li>
					<Link to="/graph">Graph</Link>
				</li>
				<li>
					<Link to="/graphSVG">Graph SVG</Link>
				</li>
			</ul>
		</nav>
	);
};

export default NavBar;