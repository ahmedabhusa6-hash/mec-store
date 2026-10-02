---
updatedAt: 2026-03-16T18:20:24.000Z
---

Fetch the complete documentation index at: https://docs.bitrefill.com/llms.txt. Use this file to discover all available pages before exploring further. Append .md to any documentation page URL to get its markdown version.

# Gift Cards

Working with digital gift card products.

Gift cards are digital products with redemption codes that can be used at the respective retailer or service.

## Purchasing Gift Cards

Use the standard invoice endpoint. See [Core Concepts](https://docs.bitrefill.com/docs/core-concepts#denominations-packages-vs-ranges) for packages vs ranges.

```javascript
// Using package_id (fixed value)
const response = await fetch(`${BASE_URL}/invoices`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    products: [{ product_id: 'amazon-us', package_id: 'amazon-us<&>50', quantity: 1 }],
    payment_method: 'balance',
    auto_pay: true
  })
});

// Using value (flexible range)
const response = await fetch(`${BASE_URL}/invoices`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    products: [{ product_id: 'amazon-us', value: 75.50, quantity: 1 }],
    payment_method: 'balance',
    auto_pay: true
  })
});
```

## Redemption Info

After delivery, the order contains redemption details. See [Core Concepts](/docs/core-concepts#redemption-info) for field definitions.

| Field          | Description                    |
| -------------- | ------------------------------ |
| `code`         | Gift card code                 |
| `link`         | Redemption URL (if applicable) |
| `pin`          | PIN if required                |
| `instructions` | How to redeem                  |

<Callout theme="info">
  Not all gift cards have the same fields. Some have codes, others have links. Check what's returned and handle accordingly.
</Callout>

## Common Categories

| Category        | Examples                           |
| --------------- | ---------------------------------- |
| E-commerce      | Amazon, eBay, Walmart              |
| Gaming          | Steam, PlayStation, Xbox, Nintendo |
| Streaming       | Netflix, Spotify, Disney+          |
| Food & Delivery | Uber Eats, DoorDash, Starbucks     |

<br />