import { Container, Row, Col, Button, Form, InputGroup, Alert } from 'react-bootstrap';
import { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";

function TableRow(props) {

    function start() {

        fetch(`http://${window.location.hostname}:5000/api/users/${props.id}/attack/start`, {
            method: "POST",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
        })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "ok") {
                    props.setMessage(data.message);
                    props.setShowError(true);
                }
                else {
                    props.navigate(`/attack/${props.id}/${data.attack_id}`);
                }
            })

    };

    function seeBoat() {
        props.navigate(`/boat/${props.id}`)
    }

    return (
        <tr>
            <td className="col align-middle">{props.username}</td>
            <td className="col align-middle">
                <Button variant="outline-primary" onClick={seeBoat}>
                    See boat
                </Button></td>
            <td className="col align-middle">
                <Button variant="outline-danger" onClick={start} >
                    Attack player
                </Button>
            </td>
        </tr>
    );

}

function StartAttack() {

    const [username, setUsername] = useState('');
    const [players, setPlayers] = useState([]);
    const [showError, setShowError] = useState(false);
    const [message, setMessage] = useState('');
    const [index, setIndex] = useState(0);
    const [addPlayers, setAddPlayers] = useState(0);

    const navigate = useNavigate();

    function searchPlayer() {
        fetch(`http://${window.location.hostname}:5000/api/users/search/${username}`, {
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
        })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "ok") {
                    setPlayers([]);
                }
                else {
                    setPlayers([data.user]);
                }
            })
    }

    useEffect(() => {
        fetch(`http://${window.location.hostname}:5000/api/users?${new URLSearchParams({ page: 0 })}`, {
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
        })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "ok") {
                    setPlayers([]);
                }
                else {
                    setPlayers(data.users);
                }
            })
    }, []);

    useEffect(() => {
        fetch(`http://${window.location.hostname}:5000/api/users?${new URLSearchParams({ page: index })}`, {
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
        })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "ok") {
                    setPlayers([]);
                }
                else {
                    setPlayers(players.concat(data.users));
                }
            })
    }, [index]);

    useEffect(() => {
        if (addPlayers) {
            setIndex(index + 1);
            setAddPlayers(false);
        }
    }, [addPlayers]);

    return (
        <Container fluid className="metshige">
            <Row className="justify-content-center text-start">
                <Col xs={12} lg={6} className="bg-scroll py-5 px-5">

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

                    <h1 className="mt-3 py-3">Player list</h1>
                    <img className="m-auto w-100 py-3" alt="" src="/img/hr.png" />
                    <div className="py-3 px-5 ">
                        <div className="py-3">

                            <InputGroup>
                                <Form.Control
                                    placeholder="Username"
                                    aria-label="Username"
                                    onChange={e => setUsername(e.target.value)}
                                />
                                <Button variant="dark" onClick={searchPlayer}>
                                    Search players
                                </Button>
                            </InputGroup>
                        </div>

                        <div className="mt-3 py-3">
                            <table className="w-100 m-0 text-nowrap bg-blank">
                                <thead>
                                    <tr>
                                        <th className="col align-middle"><h3>Player</h3></th>
                                        <th className="col align-middle"><h3>Boat</h3></th>
                                        <th className="col align-middle"><h3>Attack</h3></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {players.map(p => <TableRow username={p.username} id={p.id} setMessage={setMessage} setShowError={setShowError} navigate={navigate} />)}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <img className="m-auto w-100 py-3" alt="" src="/img/hr.png" />
                    <div className="py-3">
                        <Button variant="dark" onClick={() => setAddPlayers(true)} >More player...</Button>
                    </div>
                </Col>
                <Col xs={12} lg={6}>
                    <div className="sea-1 py-5">
                        <img src="/img/ship-3.png" alt="" className="w-100 py-5" />
                    </div>
                </Col>
            </Row>
        </Container>


    );
}

export default StartAttack;