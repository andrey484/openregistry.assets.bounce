# -*- coding: utf-8 -*-
from openregistry.assets.core.utils import (
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
)
from openregistry.assets.core.utils import (
    save_asset, opassetsresource, apply_patch,
)
from openregistry.assets.bounce.validation import (
    validate_update_item_in_not_allowed_status,
    validate_item_data,
    validate_patch_item_data
)

post_validators = [
    validate_item_data,
    validate_update_item_in_not_allowed_status
]
patch_validators = [
    validate_patch_item_data,
    validate_update_item_in_not_allowed_status
]


@opassetsresource(name='assets:Asset Items',
                collection_path='/assets/{asset_id}/items',
                path='/assets/{asset_id}/items/{item_id}',
                _internal_type='bounce',
                description="Asset related items")
class AssetBounceItemResource(APIResource):

    @json_view(permission='view_asset')
    def collection_get(self):
        """Asset Item List"""
        collection_data = [i.serialize("view") for i in self.context.items]
        return {'data': collection_data}

    @json_view(content_type="application/json", permission='upload_asset_items', validators=post_validators)
    def collection_post(self):
        """Asset Item Upload"""
        item = self.request.validated['item']
        self.context.items.append(item)
        if save_asset(self.request):
            self.LOGGER.info('Created asset item {}'.format(item.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'asset_item_create'}, {'item_id': item.id}))
            self.request.response.status = 201
            item_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=item_route, item_id=item.id, _query={})
            return {'data': item.serialize("view")}

    @json_view(permission='view_asset')
    def get(self):
        """Asset Item Read"""
        item = self.request.validated['item']
        item_data = item.serialize("view")
        return {'data': item_data}

    @json_view(content_type="application/json", permission='upload_asset_items', validators=patch_validators)
    def patch(self):
        """Asset Item Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated asset item {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'asset_item_patch'}))
            return {'data': self.request.context.serialize("view")}
