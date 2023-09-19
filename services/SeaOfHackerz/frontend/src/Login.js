import { Container, Row, Col, Alert } from 'react-bootstrap';
import { useState } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

function Login(props) {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');

    const [message, setMessage] = useState('');
    const [showSuccess, setShowSuccess] = useState(false);
    const [showError, setShowError] = useState(false);


    function handleRegister(e) {
        e.preventDefault();
        setMessage('');

        if (username.length < 8 || username.length > 30) {
            setMessage('Username not valid');
            setShowError(true);
        }
        else if (password.length < 16 || password.length > 120) {
            setMessage('Password not valid');
            setShowError(true);
        }
        else if (password !== confirm) {
            setMessage('Password and confirm do not match');
            setShowError(true);
        }
        else {
            fetch(`http://${window.location.hostname}:5000/api/register`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({
                    username: username,
                    password: password,
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
                        setShowError(false);
                        setShowSuccess(true);
                    }
                })
        }
    }

    function handleLogin(e) {
        e.preventDefault();
        setMessage('');

        fetch(`http://${window.location.hostname}:5000/api/login`, {
            method: "POST",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
            body: JSON.stringify({
                username: username,
                password: password,
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
                    setShowError(false);
                    setShowSuccess(true);
                    props.setLogged(true);
                    props.setUsername(username);
                    props.setId(data.id);
                }
            })
    }

    return (
        <>
            <Container fluid className="py-5 bg-3 metshige">

                <Row className="justify-content-center text-center py-5">
                    <Col xs={12} md={8} className="py-5">
                        <h1 className="text-white">
                            Login or Sign up Argh!
                        </h1>
                    </Col>
                </Row>

                <Row className="justify-content-center text-center py-5">
                    <Col xs={8} md={4} className="py-5">
                        <Alert show={showSuccess} variant="success">
                            <Alert.Heading>Success!</Alert.Heading>
                            <hr />
                            <div className="d-flex justify-content-end">
                                <Button
                                    onClick={() => setShowSuccess(false)}
                                    variant="outline-success"
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
                    </Col>
                </Row>
                <Row className="justify-content-center align-items-center text-white text-center pb-5">
                    <Col xs={8} md={6} lg={4} xl={3} className="pb-5">

                        <img alt="" src="/img/scroll-top.png" className="w-100" />

                        <Form className="scroll-body" onSubmit={handleRegister}>
                            <h3 class="text-dark">Registration</h3>

                            <div className="w-80 text-center m-auto">
                                <Form.Control type="text" className="rounded-3 text-center" placeholder="Enter your username" onChange={e => setUsername(e.target.value)} />
                                <Form.Control type="password" className="rounded-3 text-center mt-3" placeholder="Create a password" onChange={e => setPassword(e.target.value)} />
                                <Form.Control type="password" className="rounded-3 text-center mt-3" placeholder="Confirm the password" onChange={e => setConfirm(e.target.value)} />

                                <Button variant="dark" className="mt-3 w-100" type="submit">
                                    REGISTER NOW
                                </Button>
                            </div>
                        </Form>
                        <img alt="" src="/img/scroll-bottom.png" className="w-100" />

                    </Col>

                    <Col xs={8} md={6} lg={4} xl={3} className="pb-5">


                        <img alt="" src="/img/scroll-top.png" className="w-100" />

                        <Form className="scroll-body py-3" onSubmit={handleLogin}>
                            <h3 class="text-dark">Login</h3>
                            <div className="w-80 text-center m-auto">
                                <Form.Control type="text" className="rounded-3 text-center" placeholder="Enter your usename" onChange={e => setUsername(e.target.value)} />
                                <Form.Control type="password" className="rounded-3 text-center mt-3" placeholder="Enter your password" onChange={e => setPassword(e.target.value)} />

                                <Button variant="dark" className="w-100 mt-3" type="submit">
                                    LOGIN NOW
                                </Button>
                            </div>
                        </Form>

                        <img alt="" src="/img/scroll-bottom.png" className="w-100" />


                    </Col>
                </Row>
            </Container >


        </>
    );
}

export default Login;