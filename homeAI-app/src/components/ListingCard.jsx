// ListingCard.jsx
import React, { useState, useEffect } from "react";
import "./styles.css";
import axios from "axios";

const ListingCard = ({ listings }) => {
  // Replace with your real user-email logic if needed
  const userEmail = localStorage.getItem("userEmail") || "test@example.com";

  // State for feedback
  const [reportedRoomIds, setReportedRoomIds] = useState([]);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [pendingReportId, setPendingReportId] = useState(null);

  // State for “More Info” modal
  const [showModal, setShowModal] = useState(false);
  const [selectedListing, setSelectedListing] = useState(null);

  const base_url= "http://76.152.120.193:8001/"

  // 1) On mount: fetch which rooms this user has reported
  useEffect(() => {
    const fetchReported = async () => {
      try {
        const res = await axios.get(
          base_url+"api/listing/get-user-feedback",
          { params: { user_email: userEmail } }
        );
        // Expecting: { reported_room_ids: [123,456,...] }
        setReportedRoomIds(res.data.reported_room_ids || []);
      } catch (err) {
        console.error("Error fetching reported rooms:", err);
      }
    };
    fetchReported();
  }, [userEmail]);

  const handleMoreInfo = (listing) => {
    setSelectedListing(listing);
    setShowModal(true);
  };

  const reportListing = (roomId) => {
    setPendingReportId(roomId);
    setIsModalOpen(true);
  };

  const confirmReport = async () => {
    try {
      await axios.post(
        base_url+"api/listing/user-feedback",
        {
          user_email: userEmail,
          comments: "",
          room_id: pendingReportId,
        }
      );
      alert("Listing reported successfully!");
      // mark this ID as reported locally so button disables immediately
      setReportedRoomIds((prev) => [...prev, pendingReportId]);
    } catch (err) {
      console.error(err);
      alert("Failed to report listing. Please try again.");
    } finally {
      setIsModalOpen(false);
      setPendingReportId(null);
    }
  };

  const cancelReport = () => {
    setIsModalOpen(false);
    setPendingReportId(null);
  };

  return (
    <div className="listings-container">
      <h3>🎯 Matched Listings</h3>
      {listings.length > 0 ? (
        listings.map((l) => {
          const images = (l.IMAGE_URL || "").split(",") || [];
          const isWhatsAppSource =
            (l.SOURCE || "").toLowerCase().includes("whatsapp");

          const alreadyReported = reportedRoomIds.includes(l.ROOM_ID);

          return (
            <div
              key={l.ROOM_ID || l.LISTING_URL}
              className="listing-card"
            >
              <h4>{l.DESCRIPTION_SUMMARY}</h4>
              <p className="listing-meta">
                {l.LOCATION} · ${l.PRICE} · {l.ROOM_TYPE}
              </p>
              <p className="listing-meta">Source: {l.SOURCE}</p>
              <p className="listing-meta">Date: {l.LISTING_DATE}</p>
              {l.BATH_COUNT && (
                <p className="listing-meta">
                  Baths: {l.BATH_COUNT}
                </p>
              )}
              {l.LAUNDRY_AVAILABLE && (
                <p className="listing-meta">
                  Laundry: {l.LAUNDRY_AVAILABLE ? "Yes" : "No"}
                </p>
              )}
              {!isWhatsAppSource && images.length > 0 && (
                <div className="image-carousel">
                  {images.slice(0, 3).map((url, i) => (
                    <img
                      key={i}
                      src={url.trim()}
                      alt={`img-${i}`}
                      className="preview-img"
                      onError={(e) => (e.target.style.display = "none")}
                    />
                  ))}
                  {images.length > 3 && <span>➡️</span>}
                </div>
              )}
              {isWhatsAppSource && l.IMAGE_URL && (
                <p>
                  <strong>Image URL:</strong>{" "}
                  <a
                    href={l.IMAGE_URL}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {l.IMAGE_URL}
                  </a>
                </p>
              )}

              <button
                className="more-info"
                onClick={() => handleMoreInfo(l)}
              >
                More Info
              </button>

              <button
                className="report"
                onClick={() => reportListing(l.ROOM_ID)}
                disabled={alreadyReported}
              >
                {alreadyReported
                  ? "Reported"
                  : "Report as Inactive"}
              </button>
            </div>
          );
        })
      ) : (
        <p>No listings match your criteria.</p>
      )}

      {/* Report Confirmation Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <p>
              Are you sure you want to report listing #
              {pendingReportId} as inactive?
            </p>
            <div className="modal-buttons">
              <button
                className="btn-confirm"
                onClick={confirmReport}
              >
                Report
              </button>
              <button
                className="btn-cancel"
                onClick={cancelReport}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* More Info Modal */}
      {showModal && selectedListing && (
        <div
          className="modal-overlay"
          onClick={() => setShowModal(false)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <button onClick={() => setShowModal(false)}>X</button>
            <h4>{selectedListing.DESCRIPTION_SUMMARY}</h4>
            {selectedListing.SOURCE !== 'WHATSAPP' && <p>
              <strong>URL:</strong>{" "}
              <a
                href={selectedListing.LISTING_URL}
                target="_blank"
                rel="noopener noreferrer"
              >
                {selectedListing.LISTING_URL}
              </a>
            </p>}
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
