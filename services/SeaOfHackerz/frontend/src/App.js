import { Container } from 'react-bootstrap';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import NavigationBar from './NavigationBar';
import HomePage from './HomePage';
import 'bootstrap/dist/css/bootstrap.min.css';
import Footer from './Footer';
import Login from './Login';
import Attack from './Attack';
import StartAttack from './StartAttack';
import Boat from './Boat';
import ViewBoat from './ViewBoat';

function App() {

  const [logged, setLogged] = useState(false);
  const [username, setUsername] = useState('');
  const [id, setId] = useState(-1);

  return (
    <>
      <HashRouter>
        <NavigationBar logged={logged} setLogged={setLogged} username={username} setUsername={setUsername} setId={setId} />
        <Container fluid className='no-borders mt-5'>
          <Routes>
            <Route path="/" element={<HomePage logged={logged} />} />
            <Route path="/login" element={<Login setLogged={setLogged} setUsername={setUsername} setId={setId} />} />
            <Route path="/boat" element={<Boat id={id} />} />
            <Route path="/boat/:userId" element={<ViewBoat />} />
            <Route path="/attack" element={<StartAttack />} />
            <Route path="/attack/:userId/:attackId" element={<Attack />} />
          </Routes>
        </Container>
        <Footer />
      </HashRouter>
    </>
  );
}

export default App;
