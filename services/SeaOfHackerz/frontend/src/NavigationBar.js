import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { useNavigate } from "react-router-dom";

function NavigationBar(props) {

    const navigate = useNavigate();

    function logout() {
        props.setLogged(false);
        props.setUsername('');
        props.setId(-1);
        document.cookie = 'session=; Max-Age=0;secure';
        navigate('/');
    }

    return (
        <Navbar fixed="top" expand="lg" className='sohnav metshige pb-5' >
            <Container fluid>
                <Navbar.Brand href="#">
                    <Container>
                        <img
                            alt=""
                            src="/logo.png"
                            width="40"
                            height="40"
                            className="d-inline-block align-center"
                        /> SeaOfHackerz <img
                            alt=""
                            src="/img/hr-short.png"
                            width="70"
                            className="d-inline-block align-center"
                        />
                    </Container>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className='me-auto'>
                        <Nav.Link as={Link} to="/">
                            Home
                        </Nav.Link>
                        {props.logged === true ?
                            <>
                                <Nav.Link as={Link} to="/boat">
                                    Your boat
                                </Nav.Link>
                                <Nav.Link as={Link} to="/attack">
                                    Start Attack
                                </Nav.Link>
                            </>

                            : <></>}
                    </Nav>

                    <Form className="d-flex text-center">

                        {props.logged === false ?
                            <>
                                <Link to="/login"><Button className="mx-2" variant="outline-dark">Log In</Button></Link>
                                <Link to="/login"><Button className="mx-2" variant="outline-dark">+ Sign Up</Button></Link>
                            </>
                            : <>
                                <Link to="/boat"><Button className="mx-2" variant="outline-dark">{props.username}</Button></Link>

                                <Button className="mx-2" variant="outline-dark" onClick={logout}>- Log out</Button>
                            </>}
                    </Form>
                </Navbar.Collapse>
            </Container>
        </Navbar>

    );
}

export default NavigationBar;