import React, { useState, useContext } from 'react';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

const initialOptions = {
  'client-id': process.env.REACT_APP_PAYPAL_CLIENT_ID,
  currency: 'USD',
  intent: 'capture',
};

export default function BuyProPage() {
  const [showPayPal, setShowPayPal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const { user, setUser, refreshUser, isAuthenticated, openLoginModal } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleUpgrade = async (paymentDetails) => {
    setIsProcessing(true);
    try {
      await api.post(
        '/user/upgrade-to-pro/',
        {
          paypal_order_id: paymentDetails.id,
          payment_status: paymentDetails.status,
          payer_id: paymentDetails.payer?.payer_id,
        },
        { withCredentials: true }
      );

      if (setUser && user) {
        setUser({ ...user, is_pro: true });
      }

      if (refreshUser) await refreshUser();

      alert('🎉 You are now a Pro user!');
      setShowPayPal(false);
      navigate('/');
    } catch (err) {
      console.error('Upgrade failed:', err);
      alert(
        'Payment succeeded but upgrade failed. Contact support with transaction ID: ' +
          paymentDetails.id
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBuyProClick = () => {
    if (!isAuthenticated) {
      openLoginModal();
      return;
    }
    setShowPayPal(true);
  };

  if (user?.is_pro) {
    return (
      <div className="min-h-screen bg-blue0 dark:bg-blue90 flex items-center justify-center px-4">
        <div className="w-full max-w-xl bg-white dark:bg-gray-900 text-center px-8 py-13 rounded-3xl shadow-xl ring-4 ring-green-500 dark:ring-green-400 border border-green-300 dark:border-green-600">
          <h1 className="text-6xl font-extrabold mb-8 text-green-600 dark:text-green-400">
            👑 You're Already A Premium User!
          </h1>
          <p className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-8">
            Enjoy all Pro features without limits.
          </p>
          <button
            onClick={() => navigate('/')}
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-xl font-bold text-lg transition shadow-md"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <PayPalScriptProvider options={initialOptions}>
      <div className="min-h-screen bg-blue0 dark:bg-blue90 flex items-center justify-center px-4 relative">
        <div className="w-full max-w-xl min-h-[75vh] bg-white dark:bg-gray-900 text-center px-7 py-7 rounded-3xl shadow-xl ring-4 ring-blue70 dark:ring-cyan-600 border border-blue50 dark:border-cyan-800">
          <h1 className="text-5xl font-extrabold mb-12 text-blue70 dark:text-cyan-300">
            Upgrade to Pro
          </h1>

          <p className="mb-12 text-xl font-semibold text-blue80 dark:text-cyan-200">
            Unlock exclusive features:
          </p>

          <ul className="text-center mb-20 space-y-12 text-lg font-medium text-blue80 dark:text-cyan-200">
            <li>Create your own custom learning tracks</li>
            <li>Smarter Task Generation, Driven by the Most Advanced AI Model </li>
            <li>Early access to new features and tools</li>
          </ul>

          <button
            className="mt-3 bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500
            text-white px-10 py-4 rounded-xl font-bold text-lg transition shadow-md disabled:opacity-50
            disabled:cursor-not-allowed"
            onClick={handleBuyProClick}
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Go Premium'}
          </button>
        </div>

        {showPayPal && (
          <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg max-w-md w-full relative">
              <h1 className="text-3xl font-bold mb-6 text-center text-gray-900 dark:text-white">
                Get Pro User Access
              </h1>
              <p className="text-center text-gray-600 dark:text-gray-300 mb-8">
                Get full access to AI-powered custom track creation.
              </p>

              <button
                className="absolute top-2 right-3 text-gray-600 dark:text-white hover:text-red-500 text-2xl font-bold"
                onClick={() => setShowPayPal(false)}
                disabled={isProcessing}
              >
                ✕
              </button>

              {isProcessing && (
                <div className="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-90 flex items-center justify-center rounded-xl">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                    <p className="text-gray-700 dark:text-gray-300">Processing your upgrade...</p>
                  </div>
                </div>
              )}

              <PayPalButtons
                style={{ layout: 'vertical', color: 'blue', shape: 'rect', label: 'paypal' }}
                disabled={isProcessing}
                createOrder={(data, actions) => {
                  return actions.order.create({
                    purchase_units: [
                      {
                        amount: { value: '9.99' },
                        description: 'CodeTracks Pro Subscription',
                      },
                    ],
                  });
                }}
                onApprove={async (data, actions) => {
                  try {
                    const details = await actions.order.capture();
                    console.log('Payment successful:', details);
                    await handleUpgrade(details);
                  } catch (err) {
                    console.error('Payment or upgrade failed:', err);
                    alert(
                      'Payment succeeded but upgrade failed. Please contact support if charged.'
                    );
                    setIsProcessing(false);
                  }
                }}
                onError={(err) => {
                  console.error('PayPal error:', err);
                  alert('Payment failed. Please try again.');
                  setIsProcessing(false);
                }}
                onCancel={() => {
                  console.log('Payment cancelled by user');
                  setIsProcessing(false);
                }}
              />
            </div>
          </div>
        )}
      </div>
    </PayPalScriptProvider>
  );
}

