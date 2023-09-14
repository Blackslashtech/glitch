import { Container } from 'react-bootstrap';
import { HashRouter, Routes, Route } from 'react-router-dom';
import NavigationBar from './NavigationBar';
import FlightMonitor from './FlightMonitor';
import HomePage from './HomePage';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <>
      <HashRouter>
        <NavigationBar />
        <Container fluid className='no-borders'>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/monitor" element={<FlightMonitor />} />
          </Routes>
        </Container>
      </HashRouter>
    </>
  );
}

export default App;
