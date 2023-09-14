import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function NavigationBar(){

    let navbar_style = {
        backgroundColor: '#a4a485',
    };

    return (
        <Navbar expand="lg" style={navbar_style} variant="warning">
            <Container fluid>
                <Navbar.Brand>
                    <Container className='nav-title'>
                        <img
                            alt=""
                            src="/logo.png"
                            width="40"
                            height="40"
                            className="d-inline-block align-center"
                        />{' '}
                        Uber Pendragon
                    </Container>
                </Navbar.Brand>
                <Nav className='me-auto'>
                    <Nav.Link as={Link} to="/">
                        Home
                    </Nav.Link>
                    <Nav.Link as={Link} to="/monitor">
                        Flight Monitor
                    </Nav.Link>                    
                </Nav>
            </Container>
        </Navbar>

    );
}

export default NavigationBar;