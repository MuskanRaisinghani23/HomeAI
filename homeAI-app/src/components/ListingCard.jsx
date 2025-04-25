import React, { useState } from "react";
import "./styles.css";

const ListingCard = ({ listings }) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedListing, setSelectedListing] = useState(null);

  const handleMoreInfo = (listing) => {
    setSelectedListing(listing);
    setShowModal(true);
  };

  const reportListing = (listing_id) => {
    console.log("Reporting listing as inactive:", listing_id);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedListing(null);
  };

  return (
    <div className="listings-container">
      <h3>🎯 Matched Listings</h3>
      {listings?.length > 0 ? (
        listings.map((l) => {
          const images = l.IMAGE_URL?.split(",") || [];
          const isWhatsAppSource = l.SOURCE?.toLowerCase().includes("whatsapp");

          return (
            <div key={l.ID || l.LISTING_URL} className="listing-card">
              <h4>{l.DESCRIPTION_SUMMARY}</h4>
              <p className="listing-meta">
                {l.LOCATION} · ${l.PRICE} · {l.ROOM_TYPE}
              </p>
              <p className="listing-meta">Source: {l.SOURCE}</p>
              <p className="listing-meta">Listing Date: {l.LISTING_DATE}</p>
              {l.BATH_COUNT && (
                <p className="listing-meta">Bath Count: {l.BATH_COUNT}</p>
              )}
              {l.LAUNDRY_AVAILABLE && (
                <p className="listing-meta">Laundry: {l.LAUNDRY_AVAILABLE}</p>
              )}
              {l.CONTACT && (
                <p className="listing-meta">Contact: {l.CONTACT}</p>
              )}
              {!isWhatsAppSource && images.length > 0 && (
                <div className="image-carousel">
                  {images.slice(0, 3).map((url, i) => (
                    <img
                      key={i}
                      src={url.trim()}
                      alt={`img-${i}`}
                      className="preview-img"
                      onError={(e) => e.target.style.display = "none"}
                    />
                  ))}
                  {images.length > 3 && <span>➡️</span>}
                </div>
              )}
              {isWhatsAppSource && l.IMAGE_URL && (
                <p>
                  <strong>Image URL:</strong>{" "}
                  <a href={l.IMAGE_URL} target="_blank" rel="noreferrer">
                    {l.IMAGE_URL}
                  </a>
                </p>
              )}
              <button className="more-info" onClick={() => handleMoreInfo(l)}>
                More Info
              </button>
              <button className="report" onClick={() => reportListing(l.ID)}>
                Report as Inactive
              </button>
            </div>
          );
        })
      ) : (
        <p>No listings yet.</p>
      )}

      {showModal && selectedListing && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button onClick={handleCloseModal}>X</button>
            <h4>{selectedListing.DESCRIPTION_SUMMARY}</h4>
            <p>
              <strong>URL:</strong>{" "}
              <a
                href={selectedListing.LISTING_URL}
                target="_blank"
                rel="noopener noreferrer"
              >
                {selectedListing.LISTING_URL}
              </a>
            </p>
            {selectedListing.OTHER_DETAILS && (
              <>
                <h5>Other Details:</h5>
                <div className="other-details-grid">
                  {Object.entries(
                    JSON.parse(selectedListing.OTHER_DETAILS)
                  ).map(([key, value]) => (
                    <div key={key} className="detail-item">
                      <strong>{key.replace(/_/g, " ")}:</strong>{" "}
                      {Array.isArray(value) ? (
                        <ul className="nested-list">
                          {value.map((v, i) => (
                            <li key={i}>{v}</li>
                          ))}
                        </ul>
                      ) : typeof value === "boolean" ? (
                        value ? (
                          "Yes"
                        ) : (
                          "No"
                        )
                      ) : (
                        value
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ListingCard;
