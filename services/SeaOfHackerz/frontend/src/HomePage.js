import { Container, Row, Col, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function HomePage(props) {
    return (<>
        <Container fluid className="pt-5 bg-1 text-white text-center metshige">
            <Row className="justify-content-center py-5">

                <Col xs={12} md={6} className="py-5">
                    <h1>Chose your boat and sail into a new adventure</h1>
                    <img alt="" src="/img/hr-white.png" className="w-100 py-5" />
                    <div>many fantastic treasures are waiting for you</div>
                    <div>who will be the best hacker of the seven seas?</div>
                    {props.logged === true ?
                        <>
                            <Link to="/attack">
                                <Button variant="light" className="w-50 mt-5" >Join the battle!</Button>
                            </Link>
                        </>
                        : <>
                            <Link to="/login">
                                <Button variant="light" className="w-50 mt-5" >Join the battle!</Button>
                            </Link>
                        </>}
                </Col>
            </Row>
            <Row className="justify-content-center mt-5">
                <Col xs={12} className="px-0">
                    <img alt="" src="/img/bottom-1.png" className="w-100 bottom-1" />
                </Col>
            </Row>

        </Container>

        <Container fluid>
            <Row className="justify-content-center align-items-center py-5">
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-40" />
                </Col>
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-30" />
                </Col>
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-20" />
                </Col>
            </Row>
        </Container>

        <Container fluid className="sea-1 text-white text-atart">
            <Row className="justify-content-center align-items-center py-5">
                <Col xs={6} className="px-0">
                    <img alt="" src="/img/ship-1.png" className="w-100" />
                </Col>
                <Col xs={2}>

                </Col>
                <Col xs={4} className="metshige">
                    <h1>Customize your boat!</h1>
                    <div>and set sail for the seven seas!</div>
                </Col>
            </Row>
        </Container>

        <Container fluid>
            <Row className="justify-content-center align-items-center py-3">
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-20" />
                </Col>
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-30" />
                </Col>
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-40" />
                </Col>
            </Row>
        </Container>

        <Container fluid className="sea-2 text-white text-center">
            <Row className="justify-content-end align-items-center py-5">
                <Col xs={4} className="metshige text-start">
                    <h1>Get rewards from victories!</h1>
                    <div>
                        defeat enemy boats and steal their treasures
                    </div>
                </Col>
                <Col xs={3}>

                </Col>
                <Col xs={3} className="px-0">
                    <img alt="" src="/img/treasure.png" className="w-100" />
                </Col>
            </Row>
        </Container>

        <Container fluid>
            <Row className="justify-content-center align-items-center py-3">
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-40" />
                </Col>
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-30" />
                </Col>
                <Col xs={4} className="text-center">
                    <img alt="" src="/img/wave.png" className="w-20" />
                </Col>
            </Row>
        </Container>

        <Container fluid className="sea-1 text-white  text-center">
            <Row className="justify-content-center align-items-center py-5">
                <Col xs={6} className="px-0">
                    <img alt="" src="/img/ship-2.png" className="w-100" />
                </Col>
                <Col xs={6} className="metshige">
                    <h1>Arrrr you ready?</h1>
                    {props.logged === true ?
                        <>
                            <Link to="/attack">
                                <Button variant="light" className="w-50 mt-5" >Join the battle!</Button>
                            </Link>
                        </>
                        : <>
                            <Link to="/login">
                                <Button variant="light" className="w-50 mt-5" >Join the battle!</Button>
                            </Link>
                        </>}
                </Col>
            </Row>
        </Container>
    </>
    );
}

export default HomePage;