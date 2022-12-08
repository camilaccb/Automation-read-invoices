# Business Understanding

## Document structure

Invoice is a structure document and there is a pattern in the information we want to retrieve (invoice number). Its always located above the bar code, is only numeric and can have blank spaces or not between numbers

In the following images we have example of it:

![exemplo1](https://user-images.githubusercontent.com/98741510/206399651-3a0dcc12-fd39-44af-b770-54a5b16f2e59.png)
![exemplo 2](https://user-images.githubusercontent.com/98741510/206399909-0b04c051-4a4b-4eff-9bcd-d254ca42e13d.png)

## How to Validate extraction

To validate extraction we need guarantee invoice number is only numeric and have exactly 44 digits (without blank spaces)

TO DISCUSS: 
- only invoices with cpf are valid, should we also vallidate if cpf is present? We always need to say our cpf if we want it in invoice, so its also a possibility to only input in application invoices we have it.
- Are the other ways to validate a invoce number online? I know its possible to check nfe.

## Application's input and output

The input of application is going to be a photo of invoice and the output is going to be the invoice number extracted. 
Its necessary to storage data extracted since it will be uploaded in an app. The upload is not necessarily at same time of application output.

TO DISCUSS:
- Is there a way to send directly to app? (Its a mobile app) 



