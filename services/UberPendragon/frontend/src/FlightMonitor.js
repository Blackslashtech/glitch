import { Container } from 'react-bootstrap';
import { useState, useEffect } from 'react';

const delay = ms => new Promise(
    resolve => setTimeout(resolve, ms)
);

function FlyingDragon(props) {
    let [dragonstyle, setDragonstyle] = useState({ visibility: 'hidden' });
    let [changed, setChanged] = useState(false);

    let kx = document.getElementById('monitorMap').offsetWidth / 2102;
    let ky = document.getElementById('monitorMap').offsetHeight / 1000;

    let startingPointX = 50 + props.ride.startX / 100 * (2102 - 200) * kx;
    let startingPointY = 100 + props.ride.startY / 100 * (1000 - 200) * ky;
    let endingPointX = 50 + props.ride.endX / 100 * (2102 - 200) * kx;
    let endingPointY = 100 + props.ride.endY / 100 * (1000 - 200) * ky;

    let diffX = endingPointX - startingPointX;
    let diffY = endingPointY - startingPointY;

    useEffect(() => {
        async function waitAndFly() {
            if (props.ready && !changed) {
                await delay(props.index * 250);
                setDragonstyle({
                    top: `${startingPointY}px`,
                    left: `${startingPointX}px`,
                    transform: `translate(${diffX}px, ${diffY}px)`,
                    transition: "10s ease-in-out",
                });
                setChanged(true);
            }
        }
        waitAndFly();
    }, [dragonstyle, props.ready, changed])

    return (
        <img src={`/dragon${props.index % 4}.svg`} style={dragonstyle} className='flying-dragon'></img>
    );
}

function FlightMonitor() {

    let [ready, setReady] = useState(false)
    let [rides, setRides] = useState([]);
    let [reload, setReload] = useState(false);

    useEffect(() => {
        async function get_rides() {
            setRides([]);
            setReady(false);
            fetch(`http://${window.location.hostname}:5000/api/rides`)
                .then(res => res.json())
                .then(data => setRides(data['rides']));
            setReady(true);
        }
        get_rides();
    }, [reload]);

    setTimeout(() => setReload(!reload), 60000)

    return (
        <Container fluid className="no-borders">
            <img src={`/monitorMap.png`} className='monitor-map' id='monitorMap'></img>
            {rides.map((r, i) => <FlyingDragon ready={ready} ride={r} index={i} key={i} />)}
        </Container>
    );
}

export default FlightMonitor;
