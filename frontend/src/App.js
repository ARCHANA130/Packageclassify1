import React, { useState } from 'react';
import Confetti from 'react-confetti';
import './App.css';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [points, setPoints] = useState(null);

  const [loading, setLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [maskedImageUrl, setMaskedImageUrl] = useState(null);
  const [showImagePopup, setShowImagePopup] = useState(false);

// In handleSubmit, after defectsData is received:


// In your popup or result display:

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setSelectedImage(file);
    if (file) {
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setPoints(null);
     
      setShowPopup(false);
    } else {
      setPreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImage) {
      alert('Please upload an image first.');
      return;
    }
    setLoading(true);
    setResult(null);
    setPoints(null);
  
    setShowPopup(false);

    const formData = new FormData();
    formData.append('file', selectedImage);

    try {
      // 1. Predict class
      const predictRes = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        body: formData
      });
      const predictData = await predictRes.json();
      setResult(predictData);

      // 2. Call detect_defects
      const defectsRes = await fetch('http://127.0.0.1:8000/detect_defects', {
        method: 'POST',
        body: formData
      });
      const defectsData = await defectsRes.json();
     
      if (defectsData.masked_image_path) {
      setMaskedImageUrl(`http://127.0.0.1:8000/${defectsData.masked_image_path}`);
    }
      // 3. Call calculate_points with predicted class and detected defect_percentages
      let material = predictData.class;
      if (material.toLowerCase() === "box") material = "wrapper"; // Map "box" to "wrapper"
      const pointsRes = await fetch('http://127.0.0.1:8000/calculate_points', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          material: material,
          damage_data: defectsData.defect_percentages
        })
      });
      const pointsData = await pointsRes.json();
      setPoints(pointsData);
      if (!pointsData.error) setShowPopup(true);
    } catch (error) {
      alert('Error: ' + error.message);
    }
    setLoading(false);
  };

  const closePopup = () => setShowPopup(false);

  return (
    <div className="App" style={{
      minHeight: '100vh',
      background: 'linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1500&q=80") center/cover no-repeat',
      color: '#fff',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <header className="App-header" style={{
        background: 'rgba(0,0,0,0.7)',
        borderRadius: '20px',
        padding: '2rem 3rem',
        boxShadow: '0 8px 32px 0 rgba(31,38,135,0.37)',
        marginBottom: '2rem'
      }}>
        <h1 style={{ fontFamily: 'cursive', fontSize: '2.5rem', marginBottom: '1rem' }}>
          Package & Damage Detection
        </h1>
        <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>
          Upload an image of your package to classify and detect any damage.
        </p>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <label htmlFor="upload-image" style={{
            background: '#ff9800',
            color: '#fff',
            padding: '0.7rem 1.5rem',
            borderRadius: '30px',
            cursor: 'pointer',
            fontWeight: 'bold',
            marginBottom: '1rem',
            boxShadow: '0 4px 14px 0 rgba(255,152,0,0.39)'
          }}>
            {selectedImage ? 'Change Image' : 'Upload Image'}
            <input
              id="upload-image"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              style={{ display: 'none' }}
            />
          </label>
          {preview && (
            <div style={{
              marginBottom: '1rem',
              border: '2px solid #fff',
              borderRadius: '15px',
              overflow: 'hidden',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
            }}>
              <img src={preview} alt="Preview" style={{ width: '250px', height: 'auto', display: 'block' }} />
            </div>
          )}
          <button type="submit" style={{
            background: 'linear-gradient(90deg, #ff9800 0%, #ff5722 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: '30px',
            padding: '0.7rem 2rem',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 4px 14px 0 rgba(255,87,34,0.25)',
            transition: 'background 0.3s'
          }}>
            {loading ? 'Processing...' : 'Classify & Calculate Points'}
          </button>
        </form>
        {result && (
          <div style={{
            marginTop: '2rem',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '15px',
            padding: '1.5rem 2rem',
            color: '#fff',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            textAlign: 'center'
          }}>
            <h2>Prediction Result</h2>
            <p>
              <strong>Class:</strong> {result.class}
            </p>
          
          </div>
        )}
        {points && points.error && (
          <div style={{
            marginTop: '2rem',
            background: 'rgba(255,0,0,0.15)',
            borderRadius: '15px',
            padding: '1.5rem 2rem',
            color: '#fff',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            textAlign: 'center'
          }}>
            <h2>Error</h2>
            <p>{points.error}</p>
          </div>
        )}
       
{showPopup && points && !points.error && (
  <div style={{
    position: 'fixed',
    top: 0, left: 0, right: 0, bottom: 0,
    background: 'rgba(0,0,0,0.6)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999
  }}>
    <Confetti
      width={window.innerWidth}
      height={window.innerHeight}
      numberOfPieces={300}
      recycle={false}
    />
    <div style={{
      background: '#fff',
      color: '#ff9800',
      padding: '2rem 3rem',
      borderRadius: '25px',
      boxShadow: '0 8px 32px 0 rgba(31,38,135,0.37)',
      textAlign: 'center',
      fontSize: '2rem',
      fontWeight: 'bold',
      animation: 'pop 0.4s',
      minWidth: '350px'
    }}>
      <span role="img" aria-label="party" style={{ fontSize: '2.5rem' }}>🎉</span>
      <div style={{ margin: '1rem 0' }}>Hurray! You earned</div>
      <div style={{ fontSize: '3rem', color: '#ff5722' }}>{points.total_score} points</div>
      <div style={{ margin: '1.5rem 0 0.5rem 0', fontSize: '1.3rem', color: '#333' }}>
        <strong>Predicted Material:</strong> {result && result.class}
      </div>
      <div style={{ margin: '1.5rem 0 0.5rem 0', fontSize: '1.1rem', color: '#333', textAlign: 'center' }}>
        <strong>Damage Details (from detection):</strong>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {points.details && Object.entries(points.details).map(([type, detail]) => (
            <li key={type} style={{ marginBottom: '0.5rem' }}>
              <span style={{ color: '#ff9800', fontWeight: 'bold' }}>{type}:</span>{' '}
              {typeof detail === 'string' ? detail : (
                <>
                  {detail.percent.toFixed(2)}% - {detail.points} pts
                </>
              )}
            </li>
          ))}
        </ul>
      </div>
      <button
        onClick={() => setShowImagePopup(true)}
        style={{
          marginTop: '1rem',
          background: '#2196f3',
          color: '#fff',
          border: 'none',
          borderRadius: '20px',
          padding: '0.5rem 2rem',
          fontSize: '1.1rem',
          fontWeight: 'bold',
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(33,150,243,0.25)'
        }}
      >
        View Detected Image
      </button>
      <button onClick={closePopup} style={{
        marginTop: '1rem',
        marginLeft: '1rem',
        background: '#ff9800',
        color: '#fff',
        border: 'none',
        borderRadius: '20px',
        padding: '0.5rem 2rem',
        fontSize: '1.2rem',
        fontWeight: 'bold',
        cursor: 'pointer',
        boxShadow: '0 2px 8px rgba(255,152,0,0.39)'
      }}>
        Close
      </button>
    </div>
  </div>
)}
{showImagePopup && maskedImageUrl && (
  <div style={{
    position: 'fixed',
    top: 0, left: 0, right: 0, bottom: 0,
    background: 'rgba(0,0,0,0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10000
  }}>
    <div style={{
      background: '#fff',
      color: '#333',
      padding: '3rem 3.5rem',
      borderRadius: '30px',
      boxShadow: '0 12px 40px 0 rgba(31,38,135,0.37)',
      textAlign: 'center',
      minWidth: '420px',
      minHeight: '420px',
      maxWidth: '90vw',
      maxHeight: '90vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <strong style={{ fontSize: '1.5rem' }}>Detected Masked Image</strong>
     
      <div style={{ margin: '2rem 0', textAlign: 'center' }}>
        <img
          src={maskedImageUrl + '?t=' + Date.now()}
          alt="Detected Masked"
          style={{
            maxWidth: '350px',
            maxHeight: '450px',
            borderRadius: '20px',
            marginTop: '1rem',
            boxShadow: '0 4px 16px rgba(0,0,0,0.18)'
          }}
        />
      </div>
      <button
        onClick={() => setShowImagePopup(false)}
        style={{
          marginTop: '1rem',
          background: '#ff9800',
          color: '#fff',
          border: 'none',
          borderRadius: '20px',
          padding: '0.7rem 2.5rem',
          fontSize: '1.2rem',
          fontWeight: 'bold',
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(255,152,0,0.39)'
        }}
      >
        Close
      </button>
    </div>
  </div>
)}
      </header>
      <footer style={{ marginTop: 'auto', color: '#ccc', fontSize: '1rem' }}>
        &copy; {new Date().getFullYear()} Package AI | Creative UI by Archana
      </footer>
    </div>
  );
}

export default App;