import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";
import api from "../api/axios";
import { AuthContext } from "../context/AuthContext";

const clientId = "ASha_O1QBvAd1YGbs2i6bTLiznXOViJNO0yYdXK9fBVv9yp_w-LNMVnssMFTNNnsxicILCEmU8z1pxwH"; // Replace with actual sandbox client ID

export default function PaymentPage() {
  const navigate = useNavigate();
  const { user, fetchUser } = useContext(AuthContext);

  const handleUpgrade = async () => {
    try {
      const res = await api.post("/upgrade_to_pro/");
      if (res.data.status === "upgraded") {
        await fetchUser();
        navigate("/"); // redirect after success
      }
    } catch (err) {
      console.error("Upgrade failed", err);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-20 pt-8 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Get Pro Access</h1>
      <p className="text-center text-gray-600 dark:text-gray-300 mb-8">
        Get full access to AI-powered custom track creation using ChatGPT.
      </p>

      <PayPalScriptProvider options={{ "client-id": clientId }}>
        <PayPalButtons
          style={{ layout: "vertical", shape: "rect", color: "blue", label: "pay" }}
          createOrder={(data, actions) => {
            return actions.order.create({
              purchase_units: [
                {
                  amount: {
                    value: "5.00", // price in USD
                  },
                },
              ],
            });
          }}
          onApprove={async (data, actions) => {
            const details = await actions.order.capture();
            console.log("Payment successful:", details);
            await handleUpgrade(); // call backend to mark user as pro
          }}
        />
      </PayPalScriptProvider>
    </div>
  );
}

