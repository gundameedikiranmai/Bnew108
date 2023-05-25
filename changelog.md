Things to look at during code migration:

1. **Domain file:**
    1. slot type: unfeaturized to any
    2. add slot mappings: custom for all, from_Entity for entity based{have to check case by case}

2. **Config file**(Changes in pipeline and policies)
    1. Rule policy: mapping policy, memoization, fallback and two-stage fallback policies are deprecated, replaced with rules.

3. **Forms** (received major makeover):

    It is moved from rasa-sdk to core, and is implemented by rules. Form activation and deactivation can be handled by converting those stories into rules.
    1. domain: forms are defined in domain file with required slots
    2. Slots: the slots mappings should be eplicitly defined in domain
    3. Customization: If we want to modify simple form behaviour, we can do so by defining validation action *FormValidationAction* and overriding functions
        1. required_slots: for dynamically generate the list
        2. net_required_slot: custom implementation of requesting net slot
        3. validation slot: validation and other logic to execute after filling the slot
        4. custom slot mapping: Define a method extract_<slot_name> for every slot that should be mapped in a custom way. 

4. **Converting all files into yml format**(config, domain, stories, nlu): 

    I installed rasa2 in separate venv for conversion scripts, some of them are removed from rasa3. Explicit slot mappings and few domain formats are changed from rasa 2 to 3, they've been modified manually.

    Rasa 3 recommends using rules to simplify stories, but using [interactive learning]{https://rasa.com/docs/rasa/writing-stories#using-interactive-learning}

    commands to convert stories and nlu:
    ```
    rasa data convert nlu -f yaml --data=./data/nlu --out=./data/nlu

    rasa data convert core -f yaml --data=./data/stories --out=./data/stories
    ```

5. **Tracker store**:
    Rasa3 has async methods for various db operations, the current implementation uses sync methods. Look into migrating them as it will be deprecated in later versions.
