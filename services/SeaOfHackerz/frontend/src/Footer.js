import { Container, Row, Col } from 'react-bootstrap';

function Footer() {
    return (
        <Container fluid className="metshige footer py-5">
            <Row className="justify-content-center text-center py-5">
                <Col xs={12}>
                    <img
                        alt=""
                        src="/logo.png"
                        width="40"
                        height="40"
                        className="d-inline-block align-center"
                    /> SeaOfHackerz
                </Col>
            </Row>

            <Row className="justify-content-center text-center text-small py-2">
                <Col xs={12} md={2}>
                    <small>Legal</small>
                </Col>
                <Col xs={12} md={2}>
                    <small>Privacy notice</small>
                </Col>
                <Col xs={12} md={2}>
                    <small>Cookie Preferences</small>
                </Col>
                <Col xs={12} md={2}>
                    <small>Privacy Choice</small>
                </Col>
                <Col xs={12}>
                    <div className="mt-3 text-center">
                        <img alt="" src="img/hr.png" className="w-80" />
                    </div>
                </Col>
            </Row>
        </Container>
    );
}

export default Footer;