import { Container, Row, Col } from 'react-bootstrap';
import { useEffect, useState } from 'react';
import { useParams } from "react-router-dom";

function ViewBoat() {

    const { userId } = useParams();

    const [hull, setHull] = useState(0);
    const [sails, setSails] = useState(0);
    const [sailsColor, setSailsColor] = useState(0);
    const [porthole, setPorthole] = useState(0);
    const [flagColor, setFlagColor] = useState(0);
    const [username, setUsername] = useState('');

    useEffect(() => {

        async function getStyle() {
            fetch(`http://${window.location.hostname}:5000/api/users/${userId}/ship`, {
                credentials: "include",
            })
                .then(res => res.json())
                .then(data => {
                    for (let d of data.ship) {
                        if (d.type === "Ship") {
                            setHull(d.id);
                        }
                        else if (d.type === "Sail") {
                            setSails(d.id);
                        }
                        else if (d.type === "Sail color") {
                            setSailsColor(d.id);
                        }
                        else if (d.type === "Porthole") {
                            setPorthole(d.id);
                        }
                        else if (d.type === "Flag color") {
                            setFlagColor(d.id);
                        }
                    };
                });
        };

        async function getUsername() {
            fetch(`http://${window.location.hostname}:5000/api/user/${userId}`, {
                credentials: "include",
            })
                .then(res => res.json())
                .then(data => {
                    setUsername(data.user);
                });
        };

        getStyle();
        getUsername();

    }, [userId])


    return (
        <Container fluid className="py-5 bg-4 metshige">
            <Row className="justify-content-center text-start py-3">
                <Col xs={8} xl={6} className="py-5">
                    <div className="boat-container w-80 position-relative m-auto">
                        <img src={`/img/boat/sails-${sails}-${sailsColor}.png`} alt="" className="boat-sails position-absolute w-100" />
                        <img src={`/img/boat/hull-${hull}.png`} alt="" className="boat-hull position-absolute w-100" />
                        <img src={`/img/boat/portholes-${porthole}.png`} alt="" className="boat-portholes position-absolute w-100" />
                        <img src={`/img/boat/flags-${flagColor}.png`} alt="" className="boat-flag position-absolute w-100 " />
                    </div>
                </Col>
                <Col xs={8} xl={4} className="py-5">
                    <h1>{username}'s boat</h1>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Ship</div>

                    <div class="m-auto text-center d-flex justify-content-around mt-3">
                        <img src="/img/boat/btn-hull-0.png" alt="" className={`cursor-pointer w-20 selected-${hull === 0 ? 1 : 0}`} />
                        <img src="/img/boat/btn-hull-1.png" alt="" className={`cursor-pointer w-20 selected-${hull === 1 ? 1 : 0}`} />
                        <img src="/img/boat/btn-hull-2.png" alt="" className={`cursor-pointer w-20 selected-${hull === 2 ? 1 : 0}`} />
                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Sail</div>

                    <div class="m-auto text-center d-flex justify-content-around mt-3">
                        <img src="/img/boat/btn-sails-0.png" alt="" className={`cursor-pointer w-20 selected-${sails === 0 ? 1 : 0}`} />
                        <img src="/img/boat/btn-sails-1.png" alt="" className={`cursor-pointer w-20 selected-${sails === 1 ? 1 : 0}`} />
                        <img src="/img/boat/btn-sails-2.png" alt="" className={`cursor-pointer w-20 selected-${sails === 2 ? 1 : 0}`} />
                        <img src="/img/boat/btn-sails-3.png" alt="" className={`cursor-pointer w-20 selected-${sails === 3 ? 1 : 0}`} />
                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Sail color</div>

                    <div class="m-auto text-center my-3">

                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-0 color-selected-${sailsColor === 0 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-1 color-selected-${sailsColor === 1 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-2 color-selected-${sailsColor === 2 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-3 color-selected-${sailsColor === 3 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-4 color-selected-${sailsColor === 4 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-5 color-selected-${sailsColor === 5 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-6 color-selected-${sailsColor === 6 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-7 color-selected-${sailsColor === 7 ? 1 : 0}`} />

                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Porthole</div>

                    <div class="m-auto text-center d-flex justify-content-around mt-3">
                        <img src="/img/boat/btn-porthole-0.png" alt="" className={`cursor-pointer w-20 selected-${porthole === 0 ? 1 : 0}`} />
                        <img src="/img/boat/btn-porthole-1.png" alt="" className={`cursor-pointer w-20 selected-${porthole === 1 ? 1 : 0}`} />
                        <img src="/img/boat/btn-porthole-2.png" alt="" className={`cursor-pointer w-20 selected-${porthole === 2 ? 1 : 0}`} />
                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Flag color</div>

                    <div class="m-auto text-center my-3">
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-0 color-selected-${flagColor === 0 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-1 color-selected-${flagColor === 1 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-2 color-selected-${flagColor === 2 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-3 color-selected-${flagColor === 3 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-4 color-selected-${flagColor === 4 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-5 color-selected-${flagColor === 5 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-6 color-selected-${flagColor === 6 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" className={`cursor-pointer m-1 w-10 bg-color-7 color-selected-${flagColor === 7 ? 1 : 0}`} />

                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                </Col>
            </Row>
        </Container>
    );
}

export default ViewBoat;