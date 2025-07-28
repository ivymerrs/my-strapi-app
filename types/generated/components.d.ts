import type { Schema, Struct } from '@strapi/strapi';

export interface DialogParentInputResponse extends Struct.ComponentSchema {
  collectionName: 'components_dialog_parent_input_responses';
  info: {
    displayName: 'ParentInputResponse';
    icon: 'microphone';
  };
  attributes: {
    child_response_template: Schema.Attribute.Blocks;
    follow_up_prompt_hint: Schema.Attribute.Text;
    next_dialog_state_id: Schema.Attribute.Text;
    parent_keywords: Schema.Attribute.JSON;
  };
}

declare module '@strapi/strapi' {
  export module Public {
    export interface ComponentSchemas {
      'dialog.parent-input-response': DialogParentInputResponse;
    }
  }
}
