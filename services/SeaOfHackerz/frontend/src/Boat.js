import { Container, Row, Col, Button, Form, Alert } from 'react-bootstrap';
import { useEffect, useState } from 'react';

function Boat(props) {

    const [message, setMessage] = useState('');
    const [showMessage, setShowMessage] = useState(false);

    const [hull, setHull] = useState(0);
    const [sails, setSails] = useState(0);
    const [sailsColor, setSailsColor] = useState(0);
    const [porthole, setPorthole] = useState(0);
    const [flagColor, setFlagColor] = useState(0);

    const [inventory, setInventory] = useState([
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
        [0, ""],
    ])

    const [hoverDescription, setHoverDescription] = useState(0);
    const [descriptions, setDescriptions] = useState([['', '']]);

    useEffect(() => {
        async function getItems() {
            let items = [];
            fetch(`http://${window.location.hostname}:5000/api/items`)
                .then(res => res.json())
                .then(data => {
                    for (let d of data.items) {
                        items = [...items, [d.name, d.description]];
                    };
                    setDescriptions(items);
                });
        };

        async function getInventory() {
            let inv = [...inventory];
            for (let i in inv) {
                inv[i][0] = 0;
            }
            fetch(`http://${window.location.hostname}:5000/api/user/items`, {
                credentials: 'include',
            })
                .then(res => res.json())
                .then(data => {
                    for (let i in data.items) {
                        inv[data.items[i].item_id][0] = 1;
                        inv[data.items[i].item_id][1] = data.items[i].personal_description;
                    }
                });
            setInventory(inv);
        };

        async function getStyle() {
            fetch(`http://${window.location.hostname}:5000/api/users/${props.id}/ship`, {
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

        getItems();
        getInventory();
        getStyle();

    }, [])

    function setInventoryItem(idx, present, descr) {
        let newInventory = [...inventory];
        newInventory[idx] = [present, descr];
        return newInventory;
    }

    function saveBoat() {
        let error = false;

        async function saveInventory() {
            let items = [];
            for (let i in inventory) {
                if (inventory[i][0] === 1) {
                    items = [...items, { id: i, personal_description: inventory[i][1] }];
                }
            }
            fetch(`http://${window.location.hostname}:5000/api/user/items`, {
                method: "POST",
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({
                    items: items,
                })
            })
                .then(res => res.json())
                .then(data => {
                    console.log(data);
                    if (data.status === "error") {
                        console.log('a')
                        setMessage("Error: " + data.message);
                        setShowMessage(true);
                        error = true;
                    }
                });
        }

        async function saveShip() {
            let styles = [
                ['Ship', hull],
                ['Sail', sails],
                ['Sail color', sailsColor],
                ['Porthole', porthole],
                ['Flag color', flagColor]
            ];
            fetch(`http://${window.location.hostname}:5000/api/user/ship`, {
                method: "PUT",
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({
                    styles: styles,
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "error") {
                        setMessage("Error: " + data.message);
                        setShowMessage(true);
                        error = true;
                    }
                });
        }

        saveInventory();
        saveShip();
        if (error === false) {
            setMessage('Ship saved!');
            setShowMessage(true);
        }
    };

    return (
        <Container fluid className="py-5 bg-4 metshige">

            <Alert show={showMessage} variant="primary">
                <Alert.Heading>{message}</Alert.Heading>
                <hr />
                <div className="d-flex justify-content-end">
                    <Button
                        onClick={() => setShowMessage(false)}
                        variant="outline-primary"
                    >
                        Close this alert
                    </Button>
                </div>
            </Alert>

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
                    <h1>Configure the boat</h1>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Ship</div>

                    <div class="m-auto text-center d-flex justify-content-around mt-3">
                        <img src="/img/boat/btn-hull-0.png" alt="" onClick={_ => setHull(0)} className={`cursor-pointer w-20 selected-${hull === 0 ? 1 : 0}`} />
                        <img src="/img/boat/btn-hull-1.png" alt="" onClick={_ => setHull(1)} className={`cursor-pointer w-20 selected-${hull === 1 ? 1 : 0}`} />
                        <img src="/img/boat/btn-hull-2.png" alt="" onClick={_ => setHull(2)} className={`cursor-pointer w-20 selected-${hull === 2 ? 1 : 0}`} />
                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Sail</div>

                    <div class="m-auto text-center d-flex justify-content-around mt-3">
                        <img src="/img/boat/btn-sails-0.png" alt="" onClick={_ => setSails(0)} className={`cursor-pointer w-20 selected-${sails === 0 ? 1 : 0}`} />
                        <img src="/img/boat/btn-sails-1.png" alt="" onClick={_ => setSails(1)} className={`cursor-pointer w-20 selected-${sails === 1 ? 1 : 0}`} />
                        <img src="/img/boat/btn-sails-2.png" alt="" onClick={_ => setSails(2)} className={`cursor-pointer w-20 selected-${sails === 2 ? 1 : 0}`} />
                        <img src="/img/boat/btn-sails-3.png" alt="" onClick={_ => setSails(3)} className={`cursor-pointer w-20 selected-${sails === 3 ? 1 : 0}`} />
                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Sail color</div>

                    <div class="m-auto text-center my-3">

                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(0)} className={`cursor-pointer m-1 w-10 bg-color-0 color-selected-${sailsColor === 0 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(1)} className={`cursor-pointer m-1 w-10 bg-color-1 color-selected-${sailsColor === 1 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(2)} className={`cursor-pointer m-1 w-10 bg-color-2 color-selected-${sailsColor === 2 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(3)} className={`cursor-pointer m-1 w-10 bg-color-3 color-selected-${sailsColor === 3 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(4)} className={`cursor-pointer m-1 w-10 bg-color-4 color-selected-${sailsColor === 4 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(5)} className={`cursor-pointer m-1 w-10 bg-color-5 color-selected-${sailsColor === 5 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(6)} className={`cursor-pointer m-1 w-10 bg-color-6 color-selected-${sailsColor === 6 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setSailsColor(7)} className={`cursor-pointer m-1 w-10 bg-color-7 color-selected-${sailsColor === 7 ? 1 : 0}`} />

                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Porthole</div>

                    <div class="m-auto text-center d-flex justify-content-around mt-3">
                        <img src="/img/boat/btn-porthole-0.png" alt="" onClick={_ => setPorthole(0)} className={`cursor-pointer w-20 selected-${porthole === 0 ? 1 : 0}`} />
                        <img src="/img/boat/btn-porthole-1.png" alt="" onClick={_ => setPorthole(1)} className={`cursor-pointer w-20 selected-${porthole === 1 ? 1 : 0}`} />
                        <img src="/img/boat/btn-porthole-2.png" alt="" onClick={_ => setPorthole(2)} className={`cursor-pointer w-20 selected-${porthole === 2 ? 1 : 0}`} />
                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Flag color</div>

                    <div class="m-auto text-center my-3">
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(0)} className={`cursor-pointer m-1 w-10 bg-color-0 color-selected-${flagColor === 0 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(1)} className={`cursor-pointer m-1 w-10 bg-color-1 color-selected-${flagColor === 1 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(2)} className={`cursor-pointer m-1 w-10 bg-color-2 color-selected-${flagColor === 2 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(3)} className={`cursor-pointer m-1 w-10 bg-color-3 color-selected-${flagColor === 3 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(4)} className={`cursor-pointer m-1 w-10 bg-color-4 color-selected-${flagColor === 4 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(5)} className={`cursor-pointer m-1 w-10 bg-color-5 color-selected-${flagColor === 5 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(6)} className={`cursor-pointer m-1 w-10 bg-color-6 color-selected-${flagColor === 6 ? 1 : 0}`} />
                        <img src="/img/color-inv.png" alt="" onClick={_ => setFlagColor(7)} className={`cursor-pointer m-1 w-10 bg-color-7 color-selected-${flagColor === 7 ? 1 : 0}`} />

                    </div>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />
                    <div className="mt-2">Inventory</div>

                    <table border="0" className="w-50 m-auto py-5 my-3">
                        <tr>
                            <td><img src="/img/inventory/inv-0.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[0][0], inventory[0][1]))} onClick={_ => setHoverDescription(0)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[0][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-1.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[1][0], inventory[1][1]))} onClick={_ => setHoverDescription(1)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[1][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-2.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[2][0], inventory[2][1]))} onClick={_ => setHoverDescription(2)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[2][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-3.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[3][0], inventory[3][1]))} onClick={_ => setHoverDescription(3)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[3][0] === 1 ? 1 : 0}`} /></td></tr><tr>
                            <td><img src="/img/inventory/inv-4.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[4][0], inventory[4][1]))} onClick={_ => setHoverDescription(4)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[4][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-5.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[5][0], inventory[5][1]))} onClick={_ => setHoverDescription(5)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[5][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-6.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[6][0], inventory[6][1]))} onClick={_ => setHoverDescription(6)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[6][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-7.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[7][0], inventory[7][1]))} onClick={_ => setHoverDescription(7)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[7][0] === 1 ? 1 : 0}`} /></td></tr><tr>
                            <td><img src="/img/inventory/inv-8.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[8][0], inventory[8][1]))} onClick={_ => setHoverDescription(8)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[8][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-9.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[9][0], inventory[9][1]))} onClick={_ => setHoverDescription(9)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[9][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-10.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[10][0], inventory[10][1]))} onClick={_ => setHoverDescription(10)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[10][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-11.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[11][0], inventory[11][1]))} onClick={_ => setHoverDescription(11)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[11][0] === 1 ? 1 : 0}`} /></td></tr><tr>
                            <td><img src="/img/inventory/inv-12.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[12][0], inventory[12][1]))} onClick={_ => setHoverDescription(12)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[12][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-13.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[13][0], inventory[13][1]))} onClick={_ => setHoverDescription(13)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[13][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-14.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[14][0], inventory[14][1]))} onClick={_ => setHoverDescription(14)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[14][0] === 1 ? 1 : 0}`} /></td>
                            <td><img src="/img/inventory/inv-15.png" alt="" onDoubleClick={_ => setInventory(setInventoryItem(hoverDescription, 1 - inventory[15][0], inventory[15][1]))} onClick={_ => setHoverDescription(15)} className={`cursor-pointer w-100 p-2 color-selected-${inventory[15][0] === 1 ? 1 : 0}`} /></td>
                        </tr>
                    </table>

                    <div className="text-center">
                        <b>{hoverDescription < descriptions.length ? descriptions[hoverDescription][0] : ''}</b>
                        <div>
                            {hoverDescription < descriptions.length ? descriptions[hoverDescription][1] : ''}
                        </div>
                    </div>

                    <Form className="mt-3">

                        <Form.Check
                            type="checkbox"
                            label="Add object to the ship inventory"
                            checked={inventory[hoverDescription][0] === 1}
                            onChange={event => setInventory(setInventoryItem(hoverDescription, event.target.checked ? 1 : 0, inventory[hoverDescription][1]))}
                        />
                        <Form.Group>
                            <Form.Label>Write a private inventory object description</Form.Label>
                            <Form.Control type="text" className="rounded-3" placeholder="Enter private description" value={inventory[hoverDescription][1]} maxLength="50"
                                onChange={event => setInventory(setInventoryItem(hoverDescription, inventory[hoverDescription][0], event.target.value))} />
                        </Form.Group>

                    </Form>

                    <img src="/img/hr.png" alt="" className="w-100 mt-3" />

                    <div className="text-center py-5">
                        <Button variant="dark" onClick={saveBoat}>Save your boat!</Button>
                    </div>

                </Col>
            </Row>
        </Container>
    );
}

export default Boat;