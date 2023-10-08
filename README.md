# Diploma work for the profession of Python developer "API Service of ordering goods for retailers".

## Description

The application is designed to automate purchases in a retail chain. The users of the service are a buyer (a manager of a retail chain who purchases goods for sale in a shop) and a supplier of goods.

**Customer (buyer):**

- The purchasing manager via API makes daily purchases from a catalogue, which
  products from several suppliers.
- It is possible to specify products from different suppliers in one order - this will
  will affect the cost of delivery.
- User can authorise, register and recover password via API.
    
**Vendor:**

- Via API informs the service about price list updates.
- Can switch on and switch off order acceptance.
- Can receive the list of completed orders (with items from its price list).


### Task

Need to develop backend part (Django) of the service of ordering goods for retail chains.

**Basic part:**
* Development of the service under the ready specification (API);
* Ability to add customisable fields (characteristics) of goods;
* Import of goods;
* Sending delivery note to administrator's email (for order fulfilment);
* Sending an order to the customer's email (confirmation of order acceptance).

**Advanced part:**
* Export of goods;
* Order administration (order status and customer notification);
* Separation of slow methods into separate processes (email, import, export).

### Source data
 
1. general description of the service
1. [Specification (API) - 1 piece](./reference/screens.md)
1. [Yaml files for importing goods - 1 piece](./data/shop1.yaml).
1. [Sample API Service for shop](./reference//netology_pd_diplom/) 

## Development Stages

Backend development is recommended to be divided into the following stages:

Basic:
1. [Create and set up the project](./reference/step-1.md)
2. [Working out the data models](./reference/step-2.md)
3. [Implementing product import](./reference/step-3.md)
4. [Implementing API views](./reference/step-4.md)
5. [Fully finished backend](./reference/step-5.md)

Advanced part (optional, if the basic part is completely ready):

6. [Implementation of forms and views of the warehouse admin](./reference/step-6-adv.md)
7. [Bringing slow methods into Celery tasks](./reference/step-7-adv.md)
8. Creating a docker file for the application


It is strongly recommended to develop using git (github/gitlab/bitbucket) with regular commits to a repository accessible to your thesis advisor. Try to commit as often as possible in order to be able to get feedback from the project manager and avoid unnecessary rewriting of the code if something needs to be corrected.

Let's examine each stage in detail.

### Stage 1: Creating and setting up the project

Achievement Criteria:

1. You have the actual code of this repository on your work computer;
2. You have a django project created and it runs without errors.

For more details on this step
[follow the link](./reference/step-1.md).

#### Stage 2: Work through the data models

Achievement Criteria:

1. Models and their complementary methods have been created.

For details on this stage
[follow the link](./reference/step-2.md).

#### Stage 3: Implement the import of goods

Achievement Criteria:

1. Created functions to load goods from attached files in Django model.
2. Loaded goods from all files for import.

For details on this step.
[follow the link](./reference/step-3.md).

### Stage 4: Implementing forms and views

Achievement Criteria:

1. Implemented Views APIs for the main [pages](./reference/screens.md) of the service (without admin):
   - Login
   - Registration
   - List of goods
   - Product card
   - Basket
   - Order Confirmation
   - Thank you for your order
   - Orders
   - Order

For details on this step
[follow the link](./reference/step-4.md).

#### Stage 5: Completely finished backend

Achievement Criteria:

1. Fully working Endpoint APIs
2. The following scenario works correctly:
   - a user can authorise;
   - it is possible to send registration data and receive registration confirmation email;
   - the user can add products from different shops to the basket;
   - the user can confirm the order by entering the delivery address;
   - user receives a confirmation email after entering the delivery address;
   - The user can go to the "Orders" page and open the created order.

For more details on this step
[follow the link](./reference/step-5.md).

## Useful materials

1. [Service Information](./reference/service.md)
2. [API Specification](./reference/api.md)
3. [Service pages description](./reference/screens.md)


## Advanced part (optional)

Prerequisite: Basic part is completely ready.

### Stage 6: Realisation of API views of the warehouse admin area.

Achievement Criteria:

1. Implemented API views for [admin pages](./reference/screens.md) of the service.


For details on this milestone
[follow the link](reference/step-6-adv.md).

#### Stage 7: Bringing slow methods into Celery tasks

Achievement criteria:

1. Celery application with methods:
   - send_email
   - do_import
2. Created view to run Celery task do_import from the admin area.

For more details on this step
[follow the link](reference/step-7-adv.md).  


#### Step 8: Create a docker file for the application
1. Create a docker file to build the application.
2. Provide instructions for building the docker image.
3. Create a docker-compose file to deploy the application locally (with the database and necessary services)
