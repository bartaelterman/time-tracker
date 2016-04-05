DEFAULT_INVOICE = """
<h1>Datafable</h1>
<small>Discover the untold stories in your data</small>

<h2>Supplier</h2>
<ul>
    <li>{{ company.name }}</li>
    <li>{{ company.address}}</li>
    <li>{{ company.registration_number}}</li>
    <li>{{ company.account_number}}</li>
</ul>

<h2>Customer details</h2>
<ul>
    <li>{{ customer.name }}</li>
    <li>{{ customer.address }}</li>
    <li>{{ customer.registration_number }}</li>
</ul>

<h2>Invoice details</h2>
<ul>
    <li><b>Invoice number:</b>  </li>
    <li><b>Invoice date:</b> {{ invoice_date }} </li>
    <li><b>Delivery date:</b>  </li>
</ul>

<table>
<tr><th>week</th><th>hours</th><th>hourly rate</th><th>amount</th></tr>
{% for activity in activities %}
<tr>
  <td>{{ activity.weekstart }} - {{ activity.weekend }}</td>
  <td>{{ activity.minutes / 60.0 }}</td><td>{{ project.hourly_rate }}</td>
  <td> {{ (activity.minutes / 60.0) * project.hourly_rate }}</td>
</tr>
{% endfor %}
</table>
<p>Total: {{ total }} </p>
<p>VAT 21%: {{ total * 0.21 }} </p>
<p>Total VAT included: {{ total * 1.21 }} </p>
"""