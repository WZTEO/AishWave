import { createApp } from 'vue'

createApp({
    data() {
        return {
            activeTab: 'shop',
            currentBillboardSlide: 0,
            sliderPositions: {
                games: 0,
                ecommerce: 0,
                esim: 0,
                amazon: 0
            },
            categories: {
                games: ['Fortnite', 'PUBG', 'Free Fire', 'Call of Duty'],
                ecommerce: ['Netflix USA', 'Binance Gift Card', 'Spotify UK', 'PayPal Top-Up'],
                esim: ['eSIM Global', 'eSIM Asia', 'eSIM United States', 'eSIM Africa'],
                amazon: ['Amazon Gift Card', 'Apple Gift Card', 'eBay Gift Card', 'Google Play Gift Card', 'PlayStation Gift Card', 'Razer Gift Card', 'Steam Gift Card']
            },
            billboardSlides: [
                {
                    title: 'Welcome to Digital Products Shop',
                    description: 'Get the best digital products and services',
                    image: '/Screenshot 2025-03-11 100104.png'
                },
                {
                    title: 'Special Offers',
                    description: 'Save big on gaming credits and gift cards',
                    image: '/Screenshot 2025-03-11 084924.png'
                },
                {
                    title: 'New eSIM Products',
                    description: 'Travel the world, stay connected',
                    image: '/photo_2025-03-11_07-20-18.jpg'
                }
            ],
            products: {
                games: [
                    { name: 'Fortnite', image: 'https://cdn2.unrealengine.com/21br-keyart-squaddome-motd-1920x1080-1920x1080-5ce0ddc4bf64.jpg', link: '#' },
                    { name: 'PUBG', image: 'https://play-lh.googleusercontent.com/JRd05pyBH41qjgsJuWduRJpDeZG0Hnb0yjf2nWqO7VaGKL10-G5UIygxED-WNOc3pg=w240-h480-rw', link: '#' },
                    { name: 'Free Fire', image: 'https://play-lh.googleusercontent.com/XrklzOXxBTdnlE60DtBjiwI-M_vNHSC4OLjQVx04bzqxT8J9CEAqOls9F4XYtXqJDg=w240-h480-rw', link: '#' },
                    { name: 'Call of Duty', image: 'https://play-lh.googleusercontent.com/n6wcYP_p8prH35nmX0KgHhjugmGo9tdJYCoBFzllMdJ-F8lqX8XpcIdQZ5xZGVi7aQ=w240-h480-rw', link: '#' }
                ],
                ecommerce: [
                    { name: 'Netflix USA', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/1920px-Netflix_2015_logo.svg.png', link: '#' },
                    { name: 'Binance Gift Card', image: 'https://cryptologos.cc/logos/binance-coin-bnb-logo.png', link: '#' },
                    { name: 'Spotify UK', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Spotify_logo_with_text.svg/1920px-Spotify_logo_with_text.svg.png', link: '#' },
                    { name: 'PayPal Top-Up', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/PayPal.svg/2560px-PayPal.svg.png', link: '#' }
                ],
                esim: [
                    { name: 'eSIM Global', image: 'https://cdn-icons-png.flaticon.com/512/44/44386.png', link: '#' },
                    { name: 'eSIM Asia', image: 'https://cdn-icons-png.flaticon.com/512/2504/2504695.png', link: '#' },
                    { name: 'eSIM United States', image: 'https://cdn-icons-png.flaticon.com/512/4628/4628645.png', link: '#' },
                    { name: 'eSIM Africa', image: 'https://cdn-icons-png.flaticon.com/512/6195/6195412.png', link: '#' }
                ],
                amazon: [
                    { name: 'Amazon Gift Card', image: 'https://cdn.freebiesupply.com/logos/large/2x/amazon-icon-1.png', link: '#' },
                    { name: 'Apple Gift Card', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1667px-Apple_logo_black.svg.png', link: '#' },
                    { name: 'eBay Gift Card', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/EBay_logo.svg/2560px-EBay_logo.svg.png', link: '#' },
                    { name: 'Google Play Gift Card', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Google_Play_Store_badge_EN.svg/2560px-Google_Play_Store_badge_EN.svg.png', link: '#' },
                    { name: 'PlayStation Gift Card', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/2560px-PlayStation_logo.svg.png', link: '#' },
                    { name: 'Razer Gift Card', image: 'https://1000logos.net/wp-content/uploads/2020/04/Razer-Logo-2016.png', link: '#' },
                    { name: 'Steam Gift Card', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png', link: '#' }
                ]
            },
            categoryIntervals: {},
            touchStartX: null,
            touchThreshold: 50,
            isManualSliding: false,
            showCryptoView: false,
            showTradeView: false,
            showOrderView: false,
            orderStatusFilter: 'all',
            orderSearchQuery: '',
            selectedOrder: null,
            orders: [],
            tradeCardCode: '',
            cryptoAmount: 10,
            solAmount: 0.08,
            selectedCrypto: 'SOL',
            walletAddress: '',
            cryptos: [
                { symbol: 'BTC', name: 'Bitcoin', rate: 0.00025, color: '#F7931A', image: '/s_btc.webp' },
                { symbol: 'ETH', name: 'Ethereum', rate: 0.0033, color: '#627EEA', image: null },
                { symbol: 'SOL', name: 'Solana', rate: 0.08, color: '#14F195', image: null },
                { symbol: 'USDT', name: 'Tether', rate: 10, color: '#26A17B', image: '/s_usd.webp' },
                { symbol: 'TON', name: 'Toncoin', rate: 2.5, color: '#0088CC', image: null },
                { symbol: 'SUI', name: 'Sui', rate: 5.2, color: '#5FCADE', image: null },
                { symbol: 'BNB', name: 'Binance Coin', rate: 0.022, color: '#F0B90B', image: null },
                { symbol: 'XRP', name: 'XRP', rate: 16.7, color: '#23292F', image: null }
            ],
            showCryptoDropdown: false,
            fetchingRates: false,
            priceLastUpdated: null,
            activeFaq: null,
            selectedGiftCard: null,
            tradeAmount: '50',
            uploadedFileName: '',
            showProductDetailView: false,
            selectedProduct: null,
            selectedAmount: null,
            customAmount: '',
            gameAmounts: {
                'Fortnite': ['2800 V-Bucks Card - GH₵474.00', '5000 V-Bucks Card - GH₵761.00', '13500 V-Bucks Card - GH₵1,698.00'],
                'PUBG': ['60 UC - GH₵16.00', '325 UC - GH₵79.00', '660 UC - GH₵158.00', '1800 UC - GH₵390.00', '3800 UC - GH₵791.00'],
                'Free Fire': ['100 Diamonds - GH₵16.00', '210 Diamonds - GH₵30.00', '530 Diamonds - GH₵75.00', '1080 Diamonds - GH₵160.00', '2150 Diamonds - GH₵300.00'],
                'Call of Duty': ['30 CP - GH₵6.00', '80 CP - GH₵14.00', '420 CP - GH₵70.00', '880 CP - GH₵140.00', '2400 CP - GH₵360.00', '5000 CP - GH₵720.00']
            },
            gameImages: {
                'Fortnite': 'https://cdn2.unrealengine.com/21br-keyart-squaddome-motd-1920x1080-1920x1080-5ce0ddc4bf64.jpg',
                'PUBG': 'https://play-lh.googleusercontent.com/JRd05pyBH41qjgsJuWduRJpDeZG0Hnb0yjf2nWqO7VaGKL10-G5UIygxED-WNOc3pg=w240-h480-rw',
                'Free Fire': 'https://play-lh.googleusercontent.com/XrklzOXxBTdnlE60DtBjiwI-M_vNHSC4OLjQVx04bzqxT8J9CEAqOls9F4XYtXqJDg=w240-h480-rw',
                'Call of Duty': 'https://play-lh.googleusercontent.com/n6wcYP_p8prH35nmX0KgHhjugmGo9tdJYCoBFzllMdJ-F8lqX8XpcIdQZ5xZGVi7aQ=w240-h480-rw'
            },
            ecommerceAmounts: {
                'Netflix USA': ['$22 USD - GH₵340.00', '$28 USD - GH₵440.00', '$32 USD - GH₵500.00', '$55 USD - GH₵850.00'],
                'Binance Gift Card': [], 
                'Spotify UK': ['$13 USD (UK) - GH₵200.00', '$40 USD (UK) - GH₵620.00'],
                'PayPal Top-Up': [] 
            },
            ecommerceImages: {
                'Netflix USA': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/1920px-Netflix_2015_logo.svg.png',
                'Binance Gift Card': 'https://cryptologos.cc/logos/binance-coin-bnb-logo.png',
                'Spotify UK': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Spotify_logo_with_text.svg/1920px-Spotify_logo_with_text.svg.png',
                'PayPal Top-Up': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/PayPal.svg/2560px-PayPal.svg.png'
            },
            ecommerceDescriptions: {
                'Netflix USA': 'With streaming films, television, and original programming, Netflix has something for everyone. Netflix members can watch their favorite entertainment right at home and on any device they want, with no commercials. Ever. See What\'s Next.',
                'Binance Gift Card': 'Binance Gift Card is a tool that allows you to send a crypto gift card to your friends. You can send the card via social media, email, or SMS. The card can have a personalized theme, message, and amount. Once the receiver redeems the gift card code, the crypto will be visible in their Binance Wallet.',
                'Spotify UK': 'This Spotify Gift Card provides a 1-month Premium Subscription.',
                'PayPal Top-Up': 'PayPal is a global payment service that securely transfers funds from your credit card to merchants without exposing your financial details.'
            },
            ecommerceRedemption: {
                'Netflix USA': 'Download your Netflix Gift Card code.\nVisit netflix.com/redeem.\nEnter the 11-digit PIN from your gift card.\nIf you already have a Netflix account, go to your Account Page → Redeem Gift Card or Promo Code, and enter the code.\nThe balance will be added to your account.',
                'Binance Gift Card': 'On the Binance App:\nLog in to your Binance App.\nTap Profile → Gift Card → Enter Gift Card Marketplace.\nTap Redeem and enter the redemption code.\nThe funds will be credited to your Binance Wallet immediately.\n\nOn the Binance Website:\nLog into your Binance account.\nVisit the Gift Card homepage.\nEnter the redemption code and click Redeem.',
                'Spotify UK': 'Visit spotify.com/redeem. Enter the PIN code from your gift card.',
                'PayPal Top-Up': ''
            },
            ecommerceTerms: {
                'Netflix USA': 'Visit Netflix Terms of Use.',
                'Binance Gift Card': 'For more details, visit Binance Terms.',
                'Spotify UK': 'Redeemable only for full-price standalone Premium subscription months via spotify.com.\nCannot be used for discounted or group subscriptions.\nCannot be exchanged for cash or resold (unless required by law).\nMust be redeemed within 12 months of purchase, or the PIN expires.\nUsers must be 13+ years old and reside in the country of purchase.\nFor full terms, visit Spotify Gift Card Terms.',
                'PayPal Top-Up': 'By submitting this request, you authorize Your Digital Reward to provide your information to PayPal, Inc. for processing. This may include your email address or phone number. If you submit incorrect details, PayPal policy states that updates cannot be made for 30 days. PayPal is responsible for processing and securing transactions.'
            },
            activeFaqEcommerce: null,
            amazonAmounts: {
                'Amazon Gift Card': ['$5 Gift Card - GH₵80.00', '$10 Gift Card - GH₵160.00', '$20 Gift Card - GH₵300.00', '$30 Gift Card - GH₵470.00'],
                'Apple Gift Card': ['$5 Voucher - GH₵80.00', '$10 Voucher - GH₵159.00', '$20 Voucher - GH₵317.00', '$50 Voucher - GH₵791.00'],
                'PlayStation Gift Card': ['$10 PSN Card - GH₵159.00', '$25 PSN Card - GH₵396.00', '$50 PSN Card - GH₵791.00', '$100 PSN Card - GH₵1,581.00'],
                'Steam Gift Card': ['$10 Steam Card - GH₵159.00', '$20 Steam Card - GH₵317.00', '$50 Steam Card - GH₵800.00', '$75 Steam Card - GH₵1,186.00'],
                'Razer Gift Card': ['$1 PIN - GH₵16.00', '$2 PIN - GH₵32.00', '$5 PIN - GH₵80.00', '$10 PIN - GH₵159.00'],
                'eBay Gift Card': ['$10 eBay Card - GH₵159.00', '$20 eBay Card - GH₵310.00', '$50 eBay Card - GH₵800.00', '$100 eBay Card - GH₵1,600.00'],
                'Google Play Gift Card': ['$5 Voucher - GH₵80.00', '$10 Voucher - GH₵159.00', '$15 Voucher - GH₵238.00', '$50 Voucher - GH₵791.00'],
            },
            amazonImages: {
                'Amazon Gift Card': 'https://cdn.freebiesupply.com/logos/large/2x/amazon-icon-1.png',
                'Apple Gift Card': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1667px-Apple_logo_black.svg.png',
                'PlayStation Gift Card': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/2560px-PlayStation_logo.svg.png',
                'Steam Gift Card': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png',
                'Razer Gift Card': 'https://1000logos.net/wp-content/uploads/2020/04/Razer-Logo-2016.png',
                'eBay Gift Card': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/EBay_logo.svg/2560px-EBay_logo.svg.png',
                'Google Play Gift Card': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Google_Play_Store_badge_EN.svg/2560px-Google_Play_Store_badge_EN.svg.png'
            },
            eSimAmounts: {
                'eSIM Global': ['1GB, 7 Days – $10 (GH₵160)', '2GB, 15 Days – $20 (GH₵310)', '5GB, 30 Days – $40 (GH₵620)', '10GB, 30 Days – $70 (GH₵1,100)'],
                'eSIM Asia': ['1GB, 7 Days – $5 (GH₵80)', '2GB, 15 Days – $8 (GH₵130)', '10GB, 30 Days – $26 (GH₵401)', '20GB, 30 Days – $41 (GH₵640)'],
                'eSIM United States': ['1GB, 7 Days – $5 (GH₵80)', '2GB, 15 Days – $10 (GH₵160)', '5GB, 30 Days – $15 (GH₵240)', '20GB, 30 Days – $31 (GH₵490)'],
                'eSIM Africa': ['1GB, 7 Days – $12 (GH₵190)', '2GB, 15 Days – $20 (GH₵310)', '5GB, 30 Days – $36 (GH₵570)', '10GB, 30 Days – $65 (GH₵1,000)']
            },
            eSimDescriptions: {
                'eSIM Global': 'Stay connected to the internet wherever you go. Avoid roaming costs or hidden fees. You will receive a QR Code and activation code to install the eSIM on your device. This eSIM works globally in 106 countries.',
                'eSIM Asia': 'Stay connected to the internet wherever you go. Avoid roaming costs or hidden fees. You will receive a QR Code and activation code to install the eSIM on your device. This eSIM works in the following countries: Australia, Hong Kong, Indonesia, Macau, Malaysia, Pakistan, South Korea, Singapore, Sri Lanka, Taiwan, Thailand, Uzbekistan, Vietnam.',
                'eSIM United States': 'Stay connected to the internet wherever you go. Avoid roaming costs or hidden fees. You will receive a QR Code and activation code to install the eSIM on your device. This eSIM works in the United States.',
                'eSIM Africa': 'Stay connected to the internet wherever you go. Avoid roaming costs or hidden fees. You will receive a QR Code and activation code to install the eSIM on your device. This eSIM works in the following African countries: Egypt, Kenya, Madagascar, Mauritius, Morocco, Nigeria, South Africa, Tanzania, Tunisia, Uganda, Zambia.'
            },
            eSimImages: {
                'eSIM Global': 'https://cdn-icons-png.flaticon.com/512/44/44386.png',
                'eSIM Asia': 'https://cdn-icons-png.flaticon.com/512/2504/2504695.png',
                'eSIM United States': 'https://cdn-icons-png.flaticon.com/512/4628/4628645.png',
                'eSIM Africa': 'https://cdn-icons-png.flaticon.com/512/6195/6195412.png'
            },
            eSimDetailedInfo: {
                'eSIM Global': {
                    description: 'After purchase, you will receive a QR Code and activation code, with instructions to install the eSIM through Settings. Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Ensure your device is compatible with eSIMs and that the eSIM you are buying covers the country or region of choice. Check if your device is compatible [here](https://zendit.io/esim-device-compatibility-list/). This eSIM works in the following countries: Aland Islands, Albania, Algeria, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahrain, Bangladesh, Belgium, Bolivia, Bosnia and Herzegovina, Botswana, Brazil, Brunei, Bulgaria, Canada, Central African Republic, Chad, Chile, China, Colombia, Costa Rica, Côte d\'Ivoire, Croatia, Cyprus, Czech Republic, Democratic Republic Of The Congo, Denmark, Ecuador, Egypt, El Salvador, Estonia, Eswatini, Finland, France, French West Indies, Gabon, Georgia, Germany, Ghana, Gibraltar, Greece, Guernsey, Guinea-Bissau, Hong Kong, Hungary, Iceland, India, Indonesia, Ireland, Isle of Man, Israel, Italy, Japan, Jersey, Jordan, Kazakhstan, Kenya, Kosovo, Kuwait, Kyrgyzstan, Latvia, Liechtenstein, Lithuania, Luxembourg, Macao, Madagascar, Malawi, Malaysia, Mali, Malta, Mexico, Moldova, Monaco, Montenegro, Morocco, Netherlands, New Zealand, Nicaragua, Niger, Nigeria, North Macedonia, Norway, Oman, Pakistan, Panama, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Republic of the Congo, Réunion, Romania, Saudi Arabia, Senegal, Serbia, Seychelles, Singapore, Slovakia, Slovenia, South Africa, South Korea, Spain, Sri Lanka, Sweden, Switzerland, Taiwan, Tanzania, Thailand, Tunisia, Turkey, Uganda, Ukraine, United Arab Emirates, United Kingdom, United States, Uruguay, Uzbekistan, Vietnam, Zambia.',
                    redemption: 'Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Follow the installation instructions [here](https://zendit.io/user-guide/esim-install-instructions/), which contains instructions for installing an eSIM on iOS and Android devices either using the QR Code or through a manual install.',
                    terms: '1. eSIMs that remain unused for 12 months will be reclaimed, and any plans on these eSIMs will be forfeited. 2. To keep an eSIM active, it must have activity (e.g., purchasing or using a plan) at least once every 12 months, which resets the 12-month expiration countdown. 3. Each eSIM can have up to 30 bundles queued simultaneously.'
                },
                'eSIM Asia': {
                    description: 'After purchase, you will receive a QR Code and activation code, with instructions to install the eSIM through Settings. Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Ensure your device is compatible with eSIMs and that the eSIM you are buying covers the country or region of choice. Check if your device is compatible [here](https://zendit.io/esim-device-compatibility-list/). This eSIM works in the following countries: Australia, Hong Kong (Special Administrative Region of China), Indonesia, Macau (Special Administrative Region of China), Malaysia, Pakistan, Republic of Korea, Singapore, Sri Lanka, Taiwan (Province of China), Thailand, Uzbekistan, Vietnam.',
                    redemption: 'Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Follow the installation instructions [here](https://zendit.io/user-guide/esim-install-instructions/), which contains instructions for installing an eSIM on iOS and Android devices either using the QR Code or through a manual install.',
                    terms: '1. eSIMs that remain unused for 12 months will be reclaimed, and any plans on these eSIMs will be forfeited. 2. To keep an eSIM active, it must have activity (e.g., purchasing or using a plan) at least once every 12 months, which resets the 12-month expiration countdown. 3. Each eSIM can have up to 30 bundles queued simultaneously.'
                },
                'eSIM United States': {
                    description: 'After purchase, you will receive a QR Code and activation code, with instructions to install the eSIM through Settings. Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Ensure your device is compatible with eSIMs and that the eSIM you are buying covers the country or region of choice. Check if your device is compatible [here](https://zendit.io/esim-device-compatibility-list/).',
                    redemption: 'Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Follow the installation instructions [here](https://zendit.io/user-guide/esim-install-instructions/), which contains instructions for installing an eSIM on iOS and Android devices either using the QR Code or through a manual install.',
                    terms: '1. eSIMs that remain unused for 12 months will be reclaimed, and any plans on these eSIMs will be forfeited. 2. To keep an eSIM active, it must have activity (e.g., purchasing or using a plan) at least once every 12 months, which resets the 12-month expiration countdown. 3. Each eSIM can have up to 30 bundles queued simultaneously.'
                },
                'eSIM Africa': {
                    description: 'After purchase, you will receive a QR Code and activation code, with instructions to install the eSIM through Settings. Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Ensure your device is compatible with eSIMs and that the eSIM you are buying covers the country or region of choice. Check if your device is compatible [here](https://zendit.io/esim-device-compatibility-list/). This eSIM works in the following countries: Egypt, Kenya, Madagascar, Mauritius, Morocco, Nigeria, South Africa, Tanzania (United Republic of), Tunisia, Uganda, Zambia.',
                    redemption: 'Set up your eSIM before traveling abroad with a strong WiFi or 4G connection. Follow the installation instructions [here](https://zendit.io/user-guide/esim-install-instructions/), which contains instructions for installing an eSIM on iOS and Android devices either using the QR Code or through a manual install.',
                    terms: '1. eSIMs that remain unused for 12 months will be reclaimed, and any plans on these eSIMs will be forfeited. 2. To keep an eSIM active, it must have activity (e.g., purchasing or using a plan) at least once every 12 months, which resets the 12-month expiration countdown. 3. Each eSIM can have up to 30 bundles queued simultaneously.'
                }
            },
            giftCardImages: {
                'Apple': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1667px-Apple_logo_black.svg.png',
                'Google Play': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Google_Play_Store_badge_EN.svg/2560px-Google_Play_Store_badge_EN.svg.png',
                'Amazon': 'https://cdn.freebiesupply.com/logos/large/2x/amazon-icon-1.png',
                'eBay': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/EBay_logo.svg/2560px-EBay_logo.svg.png',
                'PlayStation': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/2560px-PlayStation_logo.svg.png',
                'Steam': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png',
                'iTunes': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/ITunes_logo.svg/1200px-ITunes_logo.svg.png',
                'Razer': 'https://1000logos.net/wp-content/uploads/2020/04/Razer-Logo-2016.png'
            },
            playerId: '',
            recipientEmail: '',
            discountPercentage: 10,
            discounts: {
                games: 10,
                ecommerce: 5,
                amazon: 8,
                esim: 12
            },
            showTermsView: false,
            terms: [
                {
                    title: "1. Overview",
                    content: "This platform provides a range of digital products and services including game credits, gift cards, eSIM packages, cryptocurrency purchases, and an optional investment program. By using our platform, you agree to the policies and terms outlined below."
                },
                {
                    title: "2. Product Delivery and Processing Times",
                    bullets: [
                        "Instant Products: Game top-ups, subscriptions, and selected gift cards are delivered instantly or within a few minutes.",
                        "Verification Process: Some transactions may require ID verification for security. This process may take a few minutes to 1 hour.",
                        "Card Selling: Processing time for card sales is typically 1 to 5 hours depending on queue and verification.",
                        "Cryptocurrency Purchases: Crypto is sent to your wallet within a few minutes post-confirmation."
                    ]
                },
                {
                    title: "3. Investment Services",
                    content: "We offer users the opportunity to invest in professionally managed pools consisting of stock market assets and gaming tournament earnings. While our expert team carefully manages these funds, investments inherently involve risk due to market volatility. Users are advised to understand their risk tolerance and accept full responsibility for their investment choices. All investments are final and irreversible once processed."
                },
                {
                    title: "4. Refund Policy",
                    content: "All sales of digital products are final and non-refundable. Refunds are only issued in cases of failed delivery due to system error or incorrect/duplicate charges (subject to investigation)."
                },
                {
                    title: "5. Privacy Policy",
                    content: "We are committed to protecting your personal data. Information collected (e.g., email, wallet address, or ID for verification) is used only for service delivery and security and never sold or shared with third parties without consent. We follow industry-standard encryption and data protection practices."
                },
                {
                    title: "6. Payment Security",
                    content: "All payments made through our platform are encrypted using secure gateways and monitored for suspicious activity. Users are advised not to share payment details or account credentials with anyone."
                },
                {
                    title: "7. User Conduct",
                    content: "By using our platform, users agree to refrain from using fraudulent or stolen payment methods and avoid abusive or exploitative behavior. Violations may result in account suspension or legal action."
                },
                {
                    title: "8. Account Responsibility",
                    content: "Users are responsible for keeping their account credentials secure and monitoring all transactions made under their account. We are not liable for losses due to compromised accounts caused by user negligence."
                },
                {
                    title: "9. Dispute Resolution",
                    content: "If a disagreement arises regarding a purchase or investment, contact our support team first to resolve the issue. If not resolved within a reasonable time, disputes may be escalated to a third-party mediator as outlined in our service agreement."
                },
                {
                    title: "10. Policy Changes",
                    content: "We reserve the right to update this policy without prior notice. Major updates will be communicated through the app or via email. Continued use of the platform implies acceptance of the latest terms."
                }
            ],
            activePolicySection: null,
        }
    },
    mounted() {
        // Start auto-sliding for billboard
        this.billboardInterval = setInterval(this.slideBillboard, 4000);
        
        // Start auto-sliding for each category
        Object.keys(this.categories).forEach(category => {
            this.categoryIntervals[category] = setInterval(() => {
                if (!this.isManualSliding) {
                    this.slideCategory(category);
                }
            }, 3000);
        });
        
        // Fetch crypto rates when component mounts
        this.updateCryptoRates();
    },
    methods: {
        setActiveTab(tab) {
            if (tab === 'crypto') {
                this.showCryptoView = true;
                this.showTradeView = false;
                this.showOrderView = false;
                return;
            }
            if (tab === 'trade') {
                this.showTradeView = true;
                this.showCryptoView = false;
                this.showOrderView = false;
                return;
            }
            if (tab === 'orders') {
                this.showOrderView = true;
                this.showCryptoView = false;
                this.showTradeView = false;
                return;
            }
            if (tab === 'terms') {
                this.showTermsView = true;
                this.showCryptoView = false;
                this.showTradeView = false;
                this.showOrderView = false;
                return;
            }
            this.activeTab = tab;
            this.showCryptoView = false;
            this.showTradeView = false;
            this.showOrderView = false;
        },
        slideBillboard() {
            this.currentBillboardSlide = (this.currentBillboardSlide + 1) % 3;
            const slider = document.querySelector('.billboard-slider');
            if (slider) {
                slider.style.transform = `translateX(-${this.currentBillboardSlide * 100}%)`;
            }
        },
        slideCategory(category) {
            const totalItems = this.categories[category].length;
            this.sliderPositions[category] = (this.sliderPositions[category] + 1) % (totalItems - 3);
            const slider = document.querySelector(`.${category}-slider`);
            if (slider) {
                slider.style.transform = `translateX(-${this.sliderPositions[category] * (25 + 3.75)}%)`;
            }
        },
        handleProductClick(product) {
            if (product.category === 'games' || product.name in this.gameAmounts) {
                this.selectedProduct = product;
                this.showProductDetailView = true;
                this.selectedAmount = null;
                this.customAmount = '';
                this.playerId = '';
                return;
            }
            
            if (product.category === 'ecommerce' || product.name in this.ecommerceAmounts) {
                this.selectedProduct = product;
                this.showProductDetailView = true;
                this.selectedAmount = null;
                this.customAmount = '';
                this.recipientEmail = '';
                return;
            }
            
            if (product.category === 'amazon' || product.name in this.amazonAmounts) {
                this.selectedProduct = product;
                this.showProductDetailView = true;
                this.selectedAmount = null;
                this.customAmount = '';
                this.recipientEmail = '';
                return;
            }
            
            if (product.category === 'esim' || product.name in this.eSimAmounts) {
                this.selectedProduct = product;
                this.showProductDetailView = true;
                this.selectedAmount = null;
                this.customAmount = '';
                this.recipientEmail = '';
                return;
            }
            
            if (product.link) {
                window.location.href = product.link;
            }
        },
        startTouchSlide(category, event) {
            this.touchStartX = event.touches[0].clientX;
            this.isManualSliding = true;
            // Clear any existing intervals
            clearInterval(this.categoryIntervals[category]);
        },
        moveTouchSlide(category, event) {
            if (!this.touchStartX) return;
            
            const touchMoveX = event.touches[0].clientX;
            const diffX = this.touchStartX - touchMoveX;
            
            const slider = document.querySelector(`.${category}-slider`);
            if (slider) {
                // Adjust slider position based on touch movement
                const currentPosition = this.sliderPositions[category] || 0;
                const newPosition = currentPosition + (diffX > 0 ? 1 : -1);
                
                // Ensure position stays within bounds
                const totalItems = this.categories[category].length;
                this.sliderPositions[category] = Math.max(0, Math.min(newPosition, totalItems - 4));
                
                slider.style.transform = `translateX(-${this.sliderPositions[category] * (25 + 3.75)}%)`;
            }
            
            this.touchStartX = touchMoveX;
        },
        endTouchSlide(category) {
            this.touchStartX = null;
            this.isManualSliding = false;
            
            // Restart auto-sliding
            this.categoryIntervals[category] = setInterval(() => {
                if (!this.isManualSliding) {
                    this.slideCategory(category);
                }
            }, 3000);
        },
        closeCryptoView() {
            this.showCryptoView = false;
        },
        closeTradeView() {
            this.showTradeView = false;
        },
        closeOrderView() {
            this.showOrderView = false;
        },
        submitTrade() {
            if (!this.tradeCardCode) {
                alert('Please enter a card code');
                return;
            }
            if (!this.selectedGiftCard) {
                alert('Please select a gift card type');
                return;
            }
            alert(`Processing trade with ${this.selectedGiftCard} card for $${this.tradeAmount}. Code: ${this.tradeCardCode}`);
        },
        selectGiftCard(cardName) {
            this.selectedGiftCard = cardName;
        },
        purchaseSolana() {
            if (!this.walletAddress) {
                alert('Please enter a wallet address');
                return;
            }
            
            const selectedCrypto = this.cryptos.find(c => c.symbol === this.selectedCrypto);
            alert(`Processing purchase of ${selectedCrypto.rate} ${selectedCrypto.symbol} to be sent to ${this.walletAddress}`);
        },
        selectCrypto(symbol) {
            this.selectedCrypto = symbol;
        },
        selectCryptoFromDropdown(symbol) {
            this.selectedCrypto = symbol;
            this.showCryptoDropdown = false;
        },
        toggleCryptoDropdown() {
            this.showCryptoDropdown = !this.showCryptoDropdown;
        },
        getCryptoAmount() {
            const crypto = this.cryptos.find(c => c.symbol === this.selectedCrypto);
            if (crypto) {
                // Calculate based on proportional exchange rate
                return ((this.cryptoAmount / 10) * crypto.rate).toFixed(8);
            }
            return 0;
        },
        updateCustomAmount(event, product) {
            this.customAmount = event.target.value;
            this.selectedAmount = this.customAmount ? `$${this.customAmount} USD - GH₵${(parseFloat(this.customAmount) * 15.8).toFixed(2)}` : null;
        },
        updateCryptoRates() {
            this.fetchingRates = true;
            
            // Using CoinGecko public API to fetch current prices
            fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,tether,the-open-network,sui,binancecoin,ripple&vs_currencies=usd')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Update rates for each crypto based on current USD price
                    const baseAmount = 10; // $10 USD
                    
                    if (data.bitcoin) this.cryptos.find(c => c.symbol === 'BTC').rate = baseAmount / data.bitcoin.usd;
                    if (data.ethereum) this.cryptos.find(c => c.symbol === 'ETH').rate = baseAmount / data.ethereum.usd;
                    if (data.solana) this.cryptos.find(c => c.symbol === 'SOL').rate = baseAmount / data.solana.usd;
                    if (data.tether) this.cryptos.find(c => c.symbol === 'USDT').rate = baseAmount / data.tether.usd;
                    if (data['the-open-network']) this.cryptos.find(c => c.symbol === 'TON').rate = baseAmount / data['the-open-network'].usd;
                    if (data.sui) this.cryptos.find(c => c.symbol === 'SUI').rate = baseAmount / data.sui.usd;
                    if (data.binancecoin) this.cryptos.find(c => c.symbol === 'BNB').rate = baseAmount / data.binancecoin.usd;
                    if (data.ripple) this.cryptos.find(c => c.symbol === 'XRP').rate = baseAmount / data.ripple.usd;
                    
                    this.priceLastUpdated = new Date().toLocaleTimeString();
                    this.fetchingRates = false;
                })
                .catch(error => {
                    console.error('Error fetching crypto rates:', error);
                    // If API fails, use a fallback method
                    this.fallbackUpdateRates();
                });
        },
        fallbackUpdateRates() {
            // Fallback method if API fails
            const newRates = {
                'BTC': 0.00025,
                'ETH': 0.0033,
                'SOL': 0.08,
                'USDT': 10,
                'TON': 2.5,
                'SUI': 5.2,
                'BNB': 0.022,
                'XRP': 16.7
            };
            
            // Update rates for each crypto
            this.cryptos.forEach(crypto => {
                if (newRates[crypto.symbol]) {
                    crypto.rate = newRates[crypto.symbol];
                }
            });
            
            this.priceLastUpdated = new Date().toLocaleTimeString() + ' (estimated)';
            this.fetchingRates = false;
        },
        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                this.uploadedFileName = file.name;
            }
        },
        toggleFaq(index) {
            this.activeFaq = this.activeFaq === index ? null : index;
        },
        toggleFaqEcommerce(section) {
            this.activeFaqEcommerce = this.activeFaqEcommerce === section ? null : section;
        },
        toggleEsimFaq(section) {
            this.activeFaqEcommerce = this.activeFaqEcommerce === section ? null : section;
        },
        filterOrders(status) {
            this.orderStatusFilter = status;
            this.selectedOrder = null;
        },
        searchOrders() {
            // Method will filter orders based on the search query
            // The actual filtering is handled in the computed property
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            return new Intl.DateTimeFormat('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                hour12: true
            }).format(date);
        },
        getOrderStatusColor(status) {
            if (status === 'pending') return '#FFB900';
            if (status === 'approved') return '#32CD32';
            if (status === 'rejected') return '#FF3B30';
            return '#777';
        },
        viewOrderDetails(order) {
            this.selectedOrder = order;
        },
        refreshOrders() {
            // In a real application, this would fetch the latest orders from the server
            alert('Refreshing order data...');
            // For demo purposes, we'll just simulate a refresh delay
            setTimeout(() => {
                alert('Orders refreshed!');
            }, 1000);
        },
        closeProductDetailView() {
            this.showProductDetailView = false;
            this.selectedProduct = null;
        },
        selectAmount(amount) {
            this.selectedAmount = amount;
            this.customAmount = '';
        },
        getOriginalAmountText(amount) {
            if (amount.includes(' - ')) {
                return amount.split(' - ')[0];
            }
            if (amount.includes(' – ')) {
                return amount.split(' – ')[0];
            }
            return amount;
        },
        getPriceFromAmount(amount) {
            if (amount.includes(' - ')) {
                return amount.split(' - ')[1];
            }
            if (amount.includes(' – ')) {
                return amount.split(' – ')[1];
            }
            return '';
        },
        getDiscountedPrice(price) {
            if (!price) return null;
            
            // Extract the numeric value from the price string
            const priceMatch = price.match(/GH₵([\d,]+\.\d{2}|[\d,]+)/);
            if (!priceMatch) return null;
            
            // Convert to number, removing commas
            const originalPrice = parseFloat(priceMatch[1].replace(/,/g, ''));
            
            // Calculate discounted price based on category
            let discount = this.discountPercentage;
            if (this.selectedProduct) {
                discount = this.discounts[this.selectedProduct.category] || this.discountPercentage;
            }
            const discountedPrice = originalPrice * (1 - discount / 100);
            
            // Format the price with commas for thousands
            return discountedPrice.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        },
        getDiscountedEsimPrice(price) {
            if (!price) return null;
            
            // Extract the numeric value from the price string, accounting for eSIM price format
            const priceMatch = price.match(/\$(\d+)\s*\(GH₵([\d,]+)\)/);
            if (!priceMatch) return null;
            
            // Get GH₵ price
            const originalPrice = parseFloat(priceMatch[2].replace(/,/g, ''));
            
            // Calculate discounted price
            const discountedPrice = originalPrice * (1 - this.discounts.esim / 100);
            
            // Format the price with commas for thousands
            return `$${priceMatch[1]} (GH₵${discountedPrice.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")})`;
        },
        purchaseGameProduct() {
            if (!this.selectedAmount) {
                alert('Please select an amount');
                return;
            }
            
            if (!this.playerId) {
                alert('Please enter your Play ID');
                return;
            }
            
            alert(`Processing purchase of ${this.selectedAmount} for ${this.selectedProduct.name} to be sent to Play ID: ${this.playerId}`);
            this.closeProductDetailView();
        },
        purchaseEcommerceProduct() {
            if (!this.selectedAmount) {
                alert('Please select an amount');
                return;
            }
            
            if (!this.recipientEmail) {
                alert('Please enter a valid email for the voucher');
                return;
            }
            
            alert(`Processing purchase of ${this.selectedAmount} for ${this.selectedProduct.name} to be sent to email: ${this.recipientEmail}`);
            this.closeProductDetailView();
        },
        purchaseEsimProduct() {
            if (!this.selectedAmount) {
                alert('Please select an amount');
                return;
            }
            
            if (!this.recipientEmail) {
                alert('Please enter a valid email to receive your eSIM');
                return;
            }
            
            alert(`Processing purchase of ${this.selectedAmount} for ${this.selectedProduct.name} to be sent to email: ${this.recipientEmail}`);
            this.closeProductDetailView();
        },
        closeTermsView() {
            this.showTermsView = false;
        },
        togglePolicy(index) {
            this.activePolicySection = this.activePolicySection === index ? null : index;
        }
    },
    computed: {
        filteredOrders() {
            let result = this.orders;

            // Filter by status if not 'all'
            if (this.orderStatusFilter !== 'all') {
                result = result.filter(order => order.status === this.orderStatusFilter);
            }

            // Filter by search query if not empty
            if (this.orderSearchQuery.trim() !== '') {
                const query = this.orderSearchQuery.toLowerCase();
                result = result.filter(order => 
                    order.id.toLowerCase().includes(query) || 
                    order.type.toLowerCase().includes(query) ||
                    (order.crypto && order.crypto.toLowerCase().includes(query)) ||
                    (order.cardType && order.cardType.toLowerCase().includes(query))
                );
            }

            return result;
        }
    }
}).mount('#app')