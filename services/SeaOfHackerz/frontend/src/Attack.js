import { Container, Row, Col, Alert } from 'react-bootstrap';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { useParams } from "react-router-dom";
import { useState } from 'react';


function Attack() {

    const { userId, attackId } = useParams();
    const [value, setValue] = useState('');
    const [showSuccess, setShowSuccess] = useState(false);
    const [showError, setShowError] = useState(false);
    const [message, setMessage] = useState('');
    const [ended, setEnded] = useState(false);

    const handleChange = event => {
        const result = event.target.value.replace(/\D/g, '');

        setValue(result);
    };

    const fire = () => {
        if (value === '') {
            setMessage('Empty guess');
            setShowError(true);
            return;
        }
        if (ended) {
            setMessage('Attack already ended');
            setShowError(true);
            setShowSuccess(false);
            return;
        }
        fetch(`http://${window.location.hostname}:5001/api/users/${userId}/attack/${attackId}`, {
            method: "POST",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
            body: JSON.stringify({
                guess: value,
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "ok") {
                    setMessage(data.message);
                    setShowError(true);
                    setShowSuccess(false);
                }
                else {
                    if (data.message === undefined) {
                        setMessage(`Attack successful! Enemy's inventory: ${JSON.stringify(data.items)}`);
                        setShowSuccess(true);
                        setEnded(true);
                    }
                    else if (data.message === "GameOver!") {
                        setMessage(data.message);
                        setEnded(true);
                        setShowError(true);
                        setShowSuccess(false);
                    }
                    else {
                        setMessage(`${data.message} The number was ${data.number}.`);
                        setShowError(false);
                        setShowSuccess(true);
                    }
                }
            })
    }

    return (
        <Container fluid className="py-5 bg-2 metshige">
            <Row className="justify-content-center text-center py-5">
                <Col xs={12}>
                    <h1 className="text-white">
                        Make your turn!
                    </h1>
                </Col>
            </Row>
            <Row className="justify-content-center text-center py-3">
                <Col xs={12} md={3}>

                    <Alert show={showSuccess} variant="primary">
                        <Alert.Heading>Attack done!</Alert.Heading>
                        <p>
                            {message}
                        </p>
                        <hr />
                        <div className="d-flex justify-content-end">
                            <Button
                                onClick={() => setShowSuccess(false)}
                                variant="outline-primary"
                            >
                                Close this alert
                            </Button>
                        </div>
                    </Alert>

                    <Alert show={showError} variant="danger">
                        <Alert.Heading>Error</Alert.Heading>
                        <p>
                            {message}
                        </p>
                        <hr />
                        <div className="d-flex justify-content-end">
                            <Button
                                onClick={() => setShowError(false)}
                                variant="outline-danger"
                            >
                                Close this alert
                            </Button>
                        </div>
                    </Alert>

                    <Form.Control type="text" className="rounded-3 text-center" placeholder="Enter your number" value={value} onChange={handleChange} />

                </Col>
            </Row>
            <Row className="justify-content-center text-center pb-5">

                <Col xs={12} md={3} className="smoke py-5">
                    <Button variant="dark" className="w-50" onClick={fire}>Fire!</Button>
                </Col>
            </Row>
        </Container>


    );
}

export default Attack;