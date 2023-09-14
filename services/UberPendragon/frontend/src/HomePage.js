import { Container, Row } from 'react-bootstrap';

function HomePage(){
    return(
        <Container fluid>
            <Row className='home-text'>
                <p className='big-font'>
                    To take advantage of our service, please use a totem at one of our stations, they will run our optimized client to book a ride on a mighty dragon.
                    {<br />}
                    Otherwise, feel free to have a look at our near-real-time flight monitor!
                </p>
            </Row>
            <Row className='parchment'>
                <svg>
                    <filter id="wavy2">
                        <feTurbulence x="0" y="0" baseFrequency="0.02" numOctaves="5" seed="1" />
                        <feDisplacementMap in="SourceGraphic" scale="20" />
                    </filter>
                </svg>
            </Row>
        </Container>
    );
}

export default HomePage;